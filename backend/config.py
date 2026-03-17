# config.py
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the application"""
    
    # LLM Provider Settings
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Model Settings
    LLM_MODELS = {
        "gemini": {
            "default": "gemini-pro",
            "vision": "gemini-1.5-pro",
            "max_tokens": 30000
        },
        "openai": {
            "default": "gpt-4-turbo-preview",
            "fast": "gpt-3.5-turbo",
            "max_tokens": 4096
        },
        "claude": {
            "default": "claude-3-opus-20240229",
            "fast": "claude-3-sonnet-20240229",
            "max_tokens": 4096
        },
        "ollama": {
            "default": "llama2",
            "alternatives": ["mistral", "codellama"],
            "max_tokens": 4096
        }
    }
    
    # Meeting Summary Settings
    # Meeting Summary Settings
    MEETING_SUMMARY_SETTINGS = {
        "max_transcript_length": 50000,
        "default_temperature": 0.3,
        "summary_temperature": 0.3,
        "insights_temperature": 0.5,
        "actions_temperature": 0.2,
        # ✅ ADD THESE:
        "summary_max_tokens": 8000,
        "insights_max_tokens": 6000,
        "actions_max_tokens": 6000,
        "email_max_tokens": 4000,
    }
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        config = {
            "provider": provider,
            "model": cls.LLM_MODELS.get(provider, {}).get("default"),
            "max_tokens": cls.LLM_MODELS.get(provider, {}).get("max_tokens", 4096)
        }
        
        if provider == "gemini":
            config["api_key"] = cls.GEMINI_API_KEY
        elif provider == "openai":
            config["api_key"] = cls.OPENAI_API_KEY
        elif provider == "claude":
            config["api_key"] = cls.ANTHROPIC_API_KEY
            
        return config