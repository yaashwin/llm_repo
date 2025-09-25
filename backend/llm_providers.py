# llm_providers.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import requests
import google.generativeai as genai
from openai import OpenAI
import anthropic
import json

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)

class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)

class OllamaProvider(LLMProvider):
    """Local Ollama provider"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False

class LLMManager:
    """Manager class to handle multiple LLM providers"""
    
    def __init__(self, default_provider: str = "gemini"):
        self.providers = {
            "gemini": GeminiProvider,
            "openai": OpenAIProvider,
            "claude": ClaudeProvider,
            "ollama": OllamaProvider
        }
        self.current_provider_name = default_provider
        self.current_provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the current provider"""
        provider_class = self.providers.get(self.current_provider_name)
        if provider_class:
            self.current_provider = provider_class()
            if not self.current_provider.is_available():
                print(f"Warning: {self.current_provider_name} provider is not properly configured")
    
    def switch_provider(self, provider_name: str, **kwargs):
        """Switch to a different LLM provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = self.providers[provider_name]
        self.current_provider = provider_class(**kwargs)
        self.current_provider_name = provider_name
        
        if not self.current_provider.is_available():
            raise Exception(f"{provider_name} provider is not properly configured")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using current provider"""
        if not self.current_provider:
            raise Exception("No LLM provider initialized")
        
        return self.current_provider.generate(prompt, **kwargs)
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Check which providers are available"""
        available = {}
        for name, provider_class in self.providers.items():
            try:
                provider = provider_class()
                available[name] = provider.is_available()
            except:
                available[name] = False
        return available