# meeting_summarizer.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import os
from abc import ABC, abstractmethod
import google.generativeai as genai
from openai import OpenAI
import anthropic
import requests

# Abstract base class for LLM providers
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
        # Always use environment variable, ignore passed api_key from frontend
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        # Always use environment variable, ignore passed api_key from frontend
        self.api_key = os.getenv("OPENAI_API_KEY")
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
        # Always use environment variable, ignore passed api_key from frontend
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
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
            raise Exception(f"{provider_name} provider is not properly configured. Please check your API key in the .env file.")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using current provider"""
        if not self.current_provider:
            raise Exception("No LLM provider initialized")
        
        if not self.current_provider.is_available():
            raise Exception(f"{self.current_provider_name} provider is not available. Please check your API key configuration.")
        
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

class MeetingSummarizer:
    """Universal meeting transcript summarizer with pluggable LLM backends"""
    
    def __init__(self, llm_provider: str = "gemini"):
        self.llm_manager = LLMManager(default_provider=llm_provider)
        
        # Common patterns to remove
        self.greeting_patterns = [
            r'\b(good\s+morning|good\s+afternoon|good\s+evening|hello|hi|hey)\b',
            r'\b(how\s+are\s+you|how\'s\s+it\s+going|what\'s\s+up)\b',
            r'\b(nice\s+to\s+see\s+you|glad\s+you\s+could\s+make\s+it)\b',
            r'\b(thank\s+you\s+for\s+joining|thanks\s+for\s+coming)\b',
        ]
        
        self.filler_patterns = [
            r'\b(um+|uh+|er+|ah+)\b',
            r'\b(like|you\s+know|I\s+mean|sort\s+of|kind\s+of)\b',
            r'\b(basically|actually|literally|obviously)\b',
            r'\b(right|okay|alright|so)\b(?=\s|,|\.|$)',
        ]
        
        self.chitchat_keywords = [
            'weather', 'weekend', 'coffee', 'lunch', 'traffic',
            'sports', 'vacation', 'holiday', 'kids', 'family',
            'yesterday', 'last night', 'this morning'
        ]
    
    def clean_transcript(self, text: str) -> str:
        """Remove greetings, fillers, and chitchat from transcript"""
        # Remove greetings (case-insensitive)
        for pattern in self.greeting_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove filler words
        for pattern in self.filler_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        text = re.sub(r'^\s*[.,!?]\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def identify_chitchat_sections(self, text: str) -> List[str]:
        """Identify potential chitchat sections"""
        sentences = text.split('.')
        chitchat_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in self.chitchat_keywords):
                # Check if it's actually business-related
                business_keywords = ['project', 'deadline', 'budget', 'client', 'meeting', 'report', 'task', 'goal']
                if not any(bk in sentence_lower for bk in business_keywords):
                    chitchat_sentences.append(sentence.strip())
        
        return chitchat_sentences
    
    def merge_transcripts(self, main_transcript: str, attachments: List[Dict[str, Any]]) -> str:
        """Merge main transcript with attachment contents"""
        merged_content = f"=== MAIN TRANSCRIPT ===\n{main_transcript}\n\n"
        
        for i, attachment in enumerate(attachments):
            merged_content += f"=== ATTACHMENT {i+1}: {attachment.get('type', 'Unknown').upper()} ===\n"
            
            if attachment.get('type') == 'url':
                merged_content += f"Source: {attachment.get('url', 'Unknown URL')}\n"
                merged_content += f"Content: {attachment.get('summary', attachment.get('text', ''))}\n\n"
            else:
                merged_content += f"{attachment.get('text', '')}\n\n"
        
        return merged_content
    
    def generate_meeting_summary(
        self,
        main_transcript: str,
        attachments: List[Dict[str, Any]] = None,
        meeting_context: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive meeting summary using LLM"""
        
        # Merge all content
        if attachments:
            merged_content = self.merge_transcripts(main_transcript, attachments)
        else:
            merged_content = main_transcript
        
        # Clean the merged content
        cleaned_content = self.clean_transcript(merged_content)
        
        # Remove chitchat sections
        chitchat = self.identify_chitchat_sections(cleaned_content)
        for chat in chitchat:
            cleaned_content = cleaned_content.replace(chat, '')
        
        # Clean up again after removing chitchat
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
        cleaned_content = cleaned_content.strip()
        
        # Prepare the prompt
        prompt = self._create_summary_prompt(cleaned_content, meeting_context, custom_instructions)
        
        try:
            # Generate summary using current LLM provider
            print(f"Generating summary with {self.llm_manager.current_provider_name}...")
            summary = self.llm_manager.generate(prompt, temperature=0.3, max_tokens=2000)
            
            # Generate additional insights
            insights_prompt = self._create_insights_prompt(cleaned_content)
            print("Generating insights...")
            insights = self.llm_manager.generate(insights_prompt, temperature=0.5, max_tokens=1500)
            
            # Extract action items
            actions_prompt = self._create_actions_prompt(cleaned_content)
            print("Extracting action items...")
            action_items = self.llm_manager.generate(actions_prompt, temperature=0.3, max_tokens=1000)
            
            return {
                "status": "success",
                "provider": self.llm_manager.current_provider_name,
                "summary": summary,
                "insights": insights,
                "action_items": action_items,
                "cleaned_transcript": cleaned_content,
                "original_length": len(merged_content),
                "cleaned_length": len(cleaned_content),
                "chitchat_removed": len(chitchat),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "provider": self.llm_manager.current_provider_name
            }
    
    def _create_summary_prompt(self, content: str, context: Optional[str], instructions: Optional[str]) -> str:
        """Create the main summary prompt"""
        prompt = f"""You are a professional meeting summarizer. Analyze the following meeting transcript and create a comprehensive summary.

{f'Meeting Context: {context}' if context else ''}
{f'Special Instructions: {instructions}' if instructions else ''}

TRANSCRIPT:
{content[:15000]}  # Limit to prevent token overflow

Please provide a structured summary with the following sections:

1. **Meeting Overview** (2-3 sentences)
   - Date, participants (if mentioned), and main purpose

2. **Key Discussion Points** (bullet points)
   - Main topics discussed
   - Important decisions made
   - Significant concerns raised

3. **Decisions and Outcomes**
   - Clear decisions that were made
   - Agreed-upon next steps

4. **Action Items** (formatted as a table)
   - Action item | Responsible person | Deadline (if mentioned)

5. **Key Takeaways**
   - 3-5 most important points from the meeting

Format the summary in a clear, professional manner. Focus on business-relevant content only."""
        
        return prompt
    
    def _create_insights_prompt(self, content: str) -> str:
        """Create prompt for generating insights"""
        return f"""Based on this meeting transcript, provide strategic insights:

TRANSCRIPT:
{content[:10000]}

Generate:
1. Potential risks or concerns that need attention
2. Opportunities identified during the discussion
3. Patterns or recurring themes
4. Recommendations for follow-up meetings

Be concise and focus on actionable insights."""
    
    def _create_actions_prompt(self, content: str) -> str:
        """Create prompt for extracting action items"""
        return f"""Extract all action items from this meeting transcript:

TRANSCRIPT:
{content[:10000]}

For each action item, identify:
- What needs to be done
- Who is responsible (if mentioned)
- Deadline or timeline (if mentioned)
- Priority level (High/Medium/Low based on context)

Format as a clear list with all available details."""
    
    def switch_provider(self, provider: str, **kwargs):
        """Switch to a different LLM provider"""
        self.llm_manager.switch_provider(provider, **kwargs)
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get list of available providers"""
        return self.llm_manager.get_available_providers()


class EnhancedMeetingSummarizer(MeetingSummarizer):
    """Enhanced meeting summarizer with template support"""
    
    def __init__(self, llm_provider: str = "gemini"):
        super().__init__(llm_provider)
        self.templates = MeetingTemplates()
    
    def generate_meeting_summary(
        self,
        main_transcript: str,
        attachments: List[Dict[str, Any]] = None,
        meeting_context: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        meeting_type: str = "general"
    ) -> Dict[str, Any]:
        """Generate meeting summary with template support"""
        
        # Get appropriate template
        template = self.templates.get_template(meeting_type)
        
        # Merge all content
        if attachments:
            merged_content = self.merge_transcripts(main_transcript, attachments)
        else:
            merged_content = main_transcript
        
        # Clean the merged content
        cleaned_content = self.clean_transcript(merged_content)
        
        # Remove chitchat sections
        chitchat = self.identify_chitchat_sections(cleaned_content)
        if chitchat:
            print(f"Removed {len(chitchat)} chitchat sections")
        
        try:
            # Generate summary using template
            summary_prompt = f"""{template['summary_prompt']}

{f'Meeting Context: {meeting_context}' if meeting_context else ''}
{f'Special Instructions: {custom_instructions}' if custom_instructions else ''}

TRANSCRIPT:
{cleaned_content[:15000]}"""
            
            summary = self.llm_manager.generate(
                summary_prompt, 
                temperature=Config.MEETING_SUMMARY_SETTINGS["summary_temperature"]
            )
            
            # Generate insights
            insights_prompt = f"""{template['insights_prompt']}

TRANSCRIPT:
{cleaned_content[:10000]}"""
            
            insights = self.llm_manager.generate(
                insights_prompt,
                temperature=Config.MEETING_SUMMARY_SETTINGS["insights_temperature"]
            )
            
            # Extract action items
            actions_prompt = f"""{template['actions_prompt']}

TRANSCRIPT:
{cleaned_content[:10000]}"""
            
            action_items = self.llm_manager.generate(
                actions_prompt,
                temperature=Config.MEETING_SUMMARY_SETTINGS["actions_temperature"]
            )
            
            # Generate email summary if requested
            email_summary = None
            if custom_instructions and "email" in custom_instructions.lower():
                email_summary = self._generate_email_summary(summary, action_items)
            
            return {
                "status": "success",
                "provider": self.llm_manager.current_provider_name,
                "meeting_type": meeting_type,
                "summary": summary,
                "insights": insights,
                "action_items": action_items,
                "email_summary": email_summary,
                "cleaned_transcript": cleaned_content,
                "original_length": len(merged_content),
                "cleaned_length": len(cleaned_content),
                "chitchat_removed": len(chitchat),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "provider": self.llm_manager.current_provider_name
            }
    
    def _generate_email_summary(self, summary: str, action_items: str) -> str:
        """Generate email-ready summary"""
        email_prompt = f"""Create a professional email summary of this meeting:

SUMMARY:
{summary}

ACTION ITEMS:
{action_items}

Format as a professional email with:
- Subject line
- Brief overview (2-3 sentences)
- Key decisions (bullet points)
- Action items (clear list)
- Next steps
- Professional closing

Keep it concise and email-appropriate."""
        
        return self.llm_manager.generate(email_prompt, temperature=0.3)