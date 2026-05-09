"""
Ultra-lightweight chat logic for memory-constrained environments.

Uses rule-based responses instead of LLM to stay under 512MB.
"""

import logging
import os
import re
from typing import List, Dict, Any

from models import Message, ChatResponse, Assessment
from retriever_simple import get_simple_retriever
from guardrails import get_guardrails

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltraLightChatLogic:
    """
    Ultra-lightweight chat logic using rule-based responses.
    
    Eliminates LLM dependency for minimal memory usage.
    """
    
    def __init__(self):
        """Initialize with rule-based logic."""
        self.retriever = get_simple_retriever()
        self.guardrails = get_guardrails()
        logger.info("Ultra-lightweight chat logic initialized (rule-based)")
    
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
        # Rule-based clarification questions
        clarification_responses = {
            "hiring": "I can help you find SHL assessments! Could you tell me more about the role? For example: What industry? What seniority level? What specific skills?",
            "test": "I'd be happy to recommend SHL assessments! Could you specify what you're testing for? For example: technical skills, personality, cognitive abilities, or specific job roles?",
            "assessment": "I can help with SHL assessments! What type of role are you hiring for? (e.g., software developer, manager, analyst, etc.)",
            "need": "I can help you find the right SHL assessments! What specific role or skills are you looking to assess?",
            "default": "I can help you find SHL assessments! Could you provide more details about the role, industry, or specific skills you'd like to assess?"
        }
        
        # Find matching response
        reply = clarification_responses.get("default")
        for key, response in clarification_responses.items():
            if key in user_query.lower():
                reply = response
                break
        
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
                assessment_details.append(assessment)
                found_assessments.append(assessment.to_assessment())
        
        if len(found_assessments) < 2:
            return ChatResponse(
                reply=f"I could only find information about {len(found_assessments)} of the assessments you mentioned. Could you clarify which specific SHL assessments you'd like to compare?",
                recommendations=found_assessments,
                end_of_conversation=False
            )
        
        # Generate comparison response
        reply = self._generate_comparison_reply(assessment_details, comparison_items)
        
        return ChatResponse(
            reply=reply,
            recommendations=found_assessments,
            end_of_conversation=False
        )
    
    def _generate_comparison_reply(self, assessments: List, items: List[str]) -> str:
        """Generate comparison response using rule-based logic."""
        if len(assessments) == 2:
            a, b = assessments
            
            # Rule-based comparison logic
            if "cognitive" in a.test_type.lower() and "personality" in b.test_type.lower():
                return f"The main difference between {a.name} and {b.name} is what they measure. {a.name} assesses cognitive abilities like reasoning and problem-solving, while {b.name} evaluates behavioral style and personality traits. Use cognitive tests for role suitability and personality tests for team fit."
            elif "technical" in a.test_type.lower() and "technical" in b.test_type.lower():
                return f"Both {a.name} and {b.name} are technical assessments. {a.name} focuses on {a.name.lower().split('test')[0]} skills, while {b.name} evaluates {b.name.lower().split('test')[0]} capabilities. Choose based on the specific technical requirements of the role."
            else:
                return f"Here's the comparison between {a.name} and {b.name}: {a.name} is a {a.test_type.lower()} assessment, while {b.name} focuses on {b.test_type.lower()}. Each serves different evaluation purposes in the hiring process."
        
        return f"I found information about {len(assessments)} assessments. Each serves different purposes: " + " | ".join([f"{ass.name} ({ass.test_type})" for ass in assessments])
    
    def _handle_refinement(self, messages: List[Message], user_query: str) -> ChatResponse:
        """Handle refinement requests based on conversation history."""
        # Extract cumulative constraints from entire conversation
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        conversation_text = " ".join(user_messages)
        
        # Search with full conversation context
        search_results = self.retriever.search(conversation_text, top_k=10)
        
        if not search_results:
            return ChatResponse(
                reply="I couldn't find assessments matching your refined criteria. Could you provide more specific details about the role or skills?",
                recommendations=[],
                end_of_conversation=False
            )
        
        # Convert to assessment format
        available_assessments = [item[0].to_assessment() for item in search_results[:8]]
        
        # Generate refinement response
        reply = self._generate_refinement_reply(user_query, available_assessments)
        
        return ChatResponse(
            reply=reply,
            recommendations=available_assessments,
            end_of_conversation=False
        )
    
    def _generate_refinement_reply(self, user_query: str, assessments: List[Assessment]) -> str:
        """Generate refinement response using rule-based logic."""
        if "personality" in user_query.lower() or "behavior" in user_query.lower():
            personality_assessments = [a for a in assessments if "personality" in a.test_type.lower() or "behavior" in a.test_type.lower()]
            if personality_assessments:
                return f"Based on your request to include personality assessments, I've updated the recommendations. Here are personality-focused options: {', '.join([a.name for a in personality_assessments[:3]])}. These will help evaluate behavioral fit and work style."
        
        if "technical" in user_query.lower() or "programming" in user_query.lower():
            tech_assessments = [a for a in assessments if "technical" in a.test_type.lower() or "programming" in a.name.lower()]
            if tech_assessments:
                return f"I've updated the recommendations to include technical assessments. Here are programming-focused options: {', '.join([a.name for a in tech_assessments[:3]])}. These will evaluate specific technical skills."
        
        return f"I've updated the recommendations based on our conversation. Here are the most relevant SHL assessments: {', '.join([a.name for a in assessments[:3]])}."
    
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
        reply = self._generate_recommendation_reply(user_query, recommended_assessments)
        
        return ChatResponse(
            reply=reply,
            recommendations=recommended_assessments,
            end_of_conversation=False
        )
    
    def _generate_recommendation_reply(self, user_query: str, assessments: List[Assessment]) -> str:
        """Generate recommendation response using rule-based logic."""
        if not assessments:
            return "I couldn't find assessments matching your criteria. Could you provide more specific details?"
        
        # Categorize assessments
        cognitive = [a for a in assessments if "cognitive" in a.test_type.lower()]
        personality = [a for a in assessments if "personality" in a.test_type.lower()]
        technical = [a for a in assessments if "technical" in a.test_type.lower()]
        
        response_parts = []
        
        if technical:
            response_parts.append(f"For technical skills, consider: {', '.join([a.name for a in technical[:2]])}")
        if cognitive:
            response_parts.append(f"For cognitive abilities, consider: {', '.join([a.name for a in cognitive[:2]])}")
        if personality:
            response_parts.append(f"For personality assessment, consider: {', '.join([a.name for a in personality[:2]])}")
        
        if not response_parts:
            response_parts.append(f"Here are relevant assessments: {', '.join([a.name for a in assessments[:3]])}")
        
        response = "Based on your needs, " + ". ".join(response_parts) + "."
        response += " Would you like me to refine these recommendations further?"
        
        return response


def get_ultra_chat_logic() -> UltraLightChatLogic:
    """Get ultra-lightweight chat logic instance."""
    return UltraLightChatLogic()
