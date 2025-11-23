# Azure OpenAI integration
import os
from openai import AzureOpenAI, OpenAI
from app.config.settings import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    def __init__(self):
        # Priority: Azure OpenAI > OpenAI regular > Mock
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
            self.enabled = True
            self.use_azure = True
            logger.info("Using Azure OpenAI")
        elif settings.OPENAI_API_KEY:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )
            self.model_name = settings.OPENAI_MODEL
            self.enabled = True
            self.use_azure = False
            logger.info(f"Using OpenAI with model: {self.model_name}")
        else:
            self.client = None
            self.enabled = False
            self.use_azure = False
            logger.warning("No AI service configured - using mock responses")
    
    async def get_chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        context_documents: Optional[List[Dict]] = None
    ) -> str:
        """
        Get chat completion from Azure OpenAI or OpenAI with optional context from search
        """
        if not self.enabled:
            return self._get_mock_response(messages, context_documents)
        
        try:
            # Add context to system message if available
            enhanced_messages = messages.copy()
            if context_documents:
                context_text = self._format_context(context_documents)
                system_message = {
                    "role": "system",
                    "content": f"""You are CivicFlow Assistant, an AI helper for civic engagement and government information.
Use the following context from official documents to answer questions:

{context_text}

Provide clear, accurate answers based on the context. If the context doesn't contain enough information, 
acknowledge this and provide general guidance."""
                }
                enhanced_messages.insert(0, system_message)
            else:
                # Add default system message
                enhanced_messages.insert(0, {
                    "role": "system",
                    "content": "You are CivicFlow Assistant, an AI helper for civic engagement and government information. Provide clear, helpful answers about local policies, regulations, and civic matters."
                })
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=enhanced_messages,
                temperature=temperature,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI API error: {str(e)}")
            return self._get_mock_response(messages, context_documents)
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format search documents as context for the AI"""
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            context_parts.append(f"[{idx}] {doc.get('title', 'Document')}:\n{doc.get('content', '')}")
        return "\n\n".join(context_parts)
    
    def _get_mock_response(self, messages: List[Dict], context_documents: Optional[List[Dict]] = None) -> str:
        """Generate mock response for development"""
        user_query = messages[-1].get("content", "")
        
        if "short-term rental" in user_query.lower() or "zone" in user_query.lower():
            return """According to the City's Zoning Ordinance, Chapter 17, Section 17.20.040, short-term rentals in Zone A are permitted but subject to specific operational standards and registration requirements. These regulations aim to balance tourism with neighborhood preservation.

Key requirements include:
- Registration with the city's Short-Term Rental Program
- Compliance with safety and building codes
- Adherence to occupancy limits
- Proof of liability insurance
- Payment of applicable taxes

Property owners must also ensure that their rentals do not negatively impact the residential character of the neighborhood."""
        
        return f"""Thank you for your question about civic matters. Based on the available information, I can help you understand local policies and regulations.

Your query: "{user_query}"

I recommend checking with the relevant city department for the most up-to-date information and specific guidance on your situation. You can also review official city documents for detailed regulations."""
