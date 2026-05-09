"""
Chat Logic module for SHL Assessment Recommender System.

This module handles the core chat functionality including:
- LLM integration (OpenRouter or Gemini)
- Conversation state management
- Response generation
- Assessment recommendations
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
import requests

from models import Message, ChatResponse, Assessment, CatalogItem
from retriever import get_retriever
from guardrails import get_guardrails
from prompts import PromptTemplates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for interacting with LLM APIs (OpenRouter or Gemini).
    
    This class handles API calls to generate responses based on prompts.
    """
    
    def __init__(self):
        """Initialize the LLM client with API configuration."""
        self.api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.base_url = None
        self.model = None
        
        if not self.api_key:
            logger.warning("No API key found. Set OPENROUTER_API_KEY or GEMINI_API_KEY environment variable.")
        
        self._configure_client()
    
    def _configure_client(self):
        """Configure the LLM client based on available API key."""
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if openrouter_key:
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
            self.model = "anthropic/claude-3-haiku"  # Fast, cost-effective model
            self.api_key = openrouter_key
            logger.info("Configured for OpenRouter API")
        elif gemini_key:
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            self.model = "gemini-flash-latest"
            self.api_key = gemini_key
            logger.info("Configured for Gemini API")
        else:
            logger.error("No valid API key found")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated response text
        """
        if not self.api_key or not self.base_url:
            return "I apologize, but the service is not properly configured. Please check the API key configuration."
        
        try:
            if "openrouter" in self.base_url:
                return self._call_openrouter(prompt)
            else:
                return self._call_gemini(prompt)
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    def _call_openrouter(self, prompt: str) -> str:
        """Make API call to OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_gemini(self, prompt: str) -> str:
        """Make API call to Gemini API."""
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 1000,
                "temperature": 0.3
            }
        }
        
        # Add API key as query parameter
        url = f"{self.base_url}?key={self.api_key}"
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]


class ChatLogic:
    """
    Core chat logic for the SHL Assessment Recommender.
    
    This class handles the main conversation flow including:
    - Processing user messages
    - Generating appropriate responses
    - Managing assessment recommendations
    - Handling different conversation scenarios
    """
    
    def __init__(self):
        """Initialize the chat logic."""
        self.llm_client = LLMClient()
        self.retriever = get_retriever()
        self.guardrails = get_guardrails()
    
    def process_message(self, messages: List[Message]) -> ChatResponse:
        """
        Process a conversation and generate a response.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            ChatResponse with reply, recommendations, and end_of_conversation flag
        """
        if not messages:
            return ChatResponse(
                reply="Hello! I'm here to help you find the right SHL assessments. What type of role are you hiring for?",
                recommendations=[],
                end_of_conversation=False
            )
        
        # Get the latest user message
        latest_message = messages[-1]
        if latest_message.role != "user":
            return ChatResponse(
                reply="I'm ready to help you with SHL assessment recommendations. What would you like to know?",
                recommendations=[],
                end_of_conversation=False
            )
        
        user_query = latest_message.content
        
        # Validate the message with guardrails
        is_valid, rejection_reason = self.guardrails.validate_conversation(messages)
        if not is_valid:
            return self._handle_refusal(user_query, rejection_reason)
        
        # Check if clarification is needed
        if self.guardrails.needs_clarification(user_query):
            return self._handle_clarification(user_query)
        
        # Check if it's a comparison request
        if self.guardrails.is_comparison_request(user_query):
            return self._handle_comparison(user_query)
        
        # Check if it's a refinement (conversation has history)
        if len(messages) > 2:
            return self._handle_refinement(messages, user_query)
        
        # Handle as a regular recommendation request
        return self._handle_recommendation(messages, user_query)
    
    def _handle_refusal(self, user_query: str, reason: str) -> ChatResponse:
        """Handle inappropriate or out-of-scope requests."""
        # Use deterministic refusal for consistency
        refusal_messages = {
            "legal": "I can only help with SHL assessments and cannot provide legal advice. For legal questions, please consult with a qualified legal professional.",
            "general_hiring": "I specialize in SHL assessments only. For general hiring advice, I recommend consulting with HR professionals or industry resources.",
            "prompt_injection": "I can only assist with SHL assessment recommendations. Please let me know what type of role or skills you'd like to assess.",
            "default": "I'm designed to help with SHL assessment recommendations only. Please ask me about assessments for specific roles or skills."
        }
        
        reply = refusal_messages.get(reason, refusal_messages["default"])
        
        return ChatResponse(
            reply=reply,
            recommendations=[],
            end_of_conversation=True
        )
    
    def _handle_clarification(self, user_query: str) -> ChatResponse:
        """Handle requests that need clarification."""
        prompt = PromptTemplates.build_clarification_prompt(user_query)
        reply = self.llm_client.generate_response(prompt)
        
        return ChatResponse(
            reply=reply,
            recommendations=[],
            end_of_conversation=False
        )
    
    def _handle_comparison(self, user_query: str) -> ChatResponse:
        """Handle assessment comparison requests."""
        # Extract assessment names to compare
        comparison_items = self.guardrails.extract_comparison_items(user_query)
        
        if len(comparison_items) < 2:
            # Not enough items to compare, treat as regular recommendation
            return self._handle_recommendation([Message(role="user", content=user_query)], user_query)
        
        # Get assessment details
        assessment_details = []
        found_assessments = []
        
        for item_name in comparison_items:
            assessment = self.retriever.get_assessment_by_name(item_name)
            if assessment:
                assessment_details.append(
                    f"{assessment.name}: {assessment.description} "
                    f"(Type: {assessment.test_type}, Duration: {assessment.duration or 'N/A'})"
                )
                found_assessments.append(assessment.to_assessment())
        
        if len(found_assessments) < 2:
            # Not enough assessments found for comparison
            return ChatResponse(
                reply=f"I could only find information about {len(found_assessments)} of the assessments you mentioned. "
                      f"Please check the assessment names or ask about specific SHL assessments.",
                recommendations=found_assessments,
                end_of_conversation=False
            )
        
        # Generate comparison response
        prompt = PromptTemplates.build_comparison_prompt(
            user_query,
            "\n".join(assessment_details)
        )
        reply = self.llm_client.generate_response(prompt)
        
        return ChatResponse(
            reply=reply,
            recommendations=found_assessments,
            end_of_conversation=False
        )
    
    def _handle_refinement(self, messages: List[Message], user_query: str) -> ChatResponse:
        """Handle refinement requests based on conversation history."""
        # Extract cumulative constraints from entire conversation
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        conversation_text = " ".join(user_messages)  # Use all user messages for context
        
        # Search with full conversation context
        search_results = self.retriever.search(conversation_text, top_k=10)
        
        # Convert to assessment format
        available_assessments = [item[0].to_assessment() for item in search_results]
        
        # Generate refinement response
        prompt = PromptTemplates.build_refinement_prompt(
            user_query,
            [msg.dict() for msg in messages],
            [item[0].dict() for item in search_results]
        )
        reply = self.llm_client.generate_response(prompt)
        
        return ChatResponse(
            reply=reply,
            recommendations=available_assessments[:10],
            end_of_conversation=False
        )
    
    def _handle_recommendation(self, messages: List[Message], user_query: str) -> ChatResponse:
        """Handle regular assessment recommendation requests."""
        # Search for relevant assessments
        search_results = self.retriever.search(user_query, top_k=10)
        
        if not search_results:
            return ChatResponse(
                reply="I couldn't find specific SHL assessments matching your query. Could you provide more details about the role or skills you're assessing?",
                recommendations=[],
                end_of_conversation=False
            )
        
        # Convert to assessment format
        recommended_assessments = [item[0].to_assessment() for item in search_results[:8]]
        
        # Generate recommendation response
        prompt = PromptTemplates.build_recommendation_prompt(
            user_query,
            [msg.dict() for msg in messages],
            [item[0].dict() for item in search_results]
        )
        reply = self.llm_client.generate_response(prompt)
        
        return ChatResponse(
            reply=reply,
            recommendations=recommended_assessments,
            end_of_conversation=False
        )


# Global chat logic instance
_chat_logic = None


def get_chat_logic() -> ChatLogic:
    """
    Get the global chat logic instance.
    
    Returns:
        ChatLogic instance
    """
    global _chat_logic
    if _chat_logic is None:
        _chat_logic = ChatLogic()
    return _chat_logic
