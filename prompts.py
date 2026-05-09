"""
Prompts module for SHL Assessment Recommender System.

This module contains system prompts and templates for generating responses
using the LLM (OpenRouter or Gemini API).
"""

from typing import List, Dict, Any


class PromptTemplates:
    """
    Contains prompt templates for different types of responses.
    
    This class provides structured prompts for the LLM to ensure consistent
    and appropriate responses for various scenarios.
    """
    
    # System prompt that defines the AI's role and constraints
    SYSTEM_PROMPT = """You are an expert SHL assessment recommender. Your role is to help users find the most suitable SHL assessments for their hiring needs.

IMPORTANT RULES:
1. ONLY recommend SHL assessments from the provided catalog
2. Always provide 1-10 relevant assessments when possible
3. Ask clarification questions for vague queries
4. Handle comparisons by comparing only catalog information
5. Handle refinements by considering conversation history
6. Refuse non-SHL related requests politely
7. Never provide legal advice or general hiring guidance
8. Keep responses concise and professional

Your response must include:
- A brief, helpful reply
- Relevant assessments from the catalog (empty list if clarifying/refusing)
- end_of_conversation flag (true only if user's need is fully met)"""

    # Template for recommendation responses
    RECOMMENDATION_TEMPLATE = """Based on your needs, here are the most suitable SHL assessments:

{context}

Previous conversation context: {conversation_history}

User query: {user_query}

Provide a helpful response with:
1. Brief explanation of why these assessments fit
2. List of recommended assessments from the catalog
3. Ask if they need more specific recommendations"""

    # Template for clarification responses
    CLARIFICATION_TEMPLATE = """I need more information to provide the best SHL assessment recommendations.

User query: {user_query}

Based on the query, please ask 1-2 specific clarification questions to help narrow down the assessment recommendations. Focus on:
- Seniority level
- Technical vs personality needs
- Specific skills or technologies
- Remote testing requirements

Return empty recommendations list since we're clarifying."""

    # Template for comparison responses
    COMPARISON_TEMPLATE = """Here's a comparison of the SHL assessments you mentioned:

{assessment_details}

User query: {user_query}

Provide a clear comparison focusing on:
- Key differences in test type and purpose
- Duration and format differences
- When to use each assessment
- Recommendations based on specific use cases"""

    # Template for refinement responses
    REFINEMENT_TEMPLATE = """Based on our conversation and your latest request, here are updated recommendations:

{context}

Conversation history: {conversation_history}
Latest refinement: {user_query}

Provide refined recommendations that:
1. Build on previous suggestions
2. Incorporate the new requirements
3. Explain why these updated recommendations are better
4. Keep the conversation focused on SHL assessments"""

    # Template for handling refusals
    REFUSAL_TEMPLATE = """I understand you're asking about: {user_query}

However, I can only help with SHL assessments and tests. 

Please note:
- I cannot provide legal advice
- I cannot give general hiring guidance
- I cannot discuss non-SHL assessments

If you're looking for SHL assessment recommendations, I'd be happy to help! Please ask about specific SHL tests or assessment needs."""

    @staticmethod
    def format_assessment_context(assessments: List[Dict[str, Any]]) -> str:
        """
        Format assessment information for the prompt context.
        
        Args:
            assessments: List of assessment dictionaries
            
        Returns:
            Formatted string with assessment details
        """
        if not assessments:
            return "No assessments found in catalog."
        
        context_lines = ["Available SHL Assessments:"]
        for i, assessment in enumerate(assessments[:10], 1):  # Limit to 10 for context
            context_lines.append(
                f"{i}. {assessment.get('name', 'Unknown')} - "
                f"{assessment.get('test_type', 'Unknown')} - "
                f"{assessment.get('description', 'No description')[:100]}..."
            )
        
        return "\n".join(context_lines)
    
    @staticmethod
    def format_conversation_history(messages: List[Dict[str, str]]) -> str:
        """
        Format conversation history for the prompt context.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted conversation history
        """
        if not messages:
            return "No previous conversation."
        
        history_lines = []
        for message in messages[-6:]:  # Last 6 messages for context
            role = message.get('role', 'unknown')
            content = message.get('content', '')[:200]  # Limit length
            history_lines.append(f"{role}: {content}")
        
        return "\n".join(history_lines)
    
    @staticmethod
    def build_recommendation_prompt(
        user_query: str,
        conversation_history: List[Dict[str, str]],
        available_assessments: List[Dict[str, Any]]
    ) -> str:
        """
        Build a complete prompt for assessment recommendations.
        
        Args:
            user_query: Current user query
            conversation_history: Previous messages
            available_assessments: Available assessments from catalog
            
        Returns:
            Complete prompt for the LLM
        """
        return f"""{PromptTemplates.SYSTEM_PROMPT}

{PromptTemplates.RECOMMENDATION_TEMPLATE.format(
            context=PromptTemplates.format_assessment_context(available_assessments),
            conversation_history=PromptTemplates.format_conversation_history(conversation_history),
            user_query=user_query
        )}"""
    
    @staticmethod
    def build_clarification_prompt(user_query: str) -> str:
        """
        Build a prompt for asking clarification questions.
        
        Args:
            user_query: Current user query
            
        Returns:
            Complete prompt for the LLM
        """
        return f"""{PromptTemplates.SYSTEM_PROMPT}

{PromptTemplates.CLARIFICATION_TEMPLATE.format(user_query=user_query)}"""
    
    @staticmethod
    def build_comparison_prompt(
        user_query: str,
        assessment_details: str
    ) -> str:
        """
        Build a prompt for comparing assessments.
        
        Args:
            user_query: Current user query
            assessment_details: Details of assessments to compare
            
        Returns:
            Complete prompt for the LLM
        """
        return f"""{PromptTemplates.SYSTEM_PROMPT}

{PromptTemplates.COMPARISON_TEMPLATE.format(
            assessment_details=assessment_details,
            user_query=user_query
        )}"""
    
    @staticmethod
    def build_refinement_prompt(
        user_query: str,
        conversation_history: List[Dict[str, str]],
        available_assessments: List[Dict[str, Any]]
    ) -> str:
        """
        Build a prompt for refining recommendations.
        
        Args:
            user_query: Current user query
            conversation_history: Previous messages
            available_assessments: Available assessments from catalog
            
        Returns:
            Complete prompt for the LLM
        """
        return f"""{PromptTemplates.SYSTEM_PROMPT}

{PromptTemplates.REFINEMENT_TEMPLATE.format(
            context=PromptTemplates.format_assessment_context(available_assessments),
            conversation_history=PromptTemplates.format_conversation_history(conversation_history),
            user_query=user_query
        )}"""
    
    @staticmethod
    def build_refusal_prompt(user_query: str) -> str:
        """
        Build a prompt for refusing inappropriate requests.
        
        Args:
            user_query: Current user query
            
        Returns:
            Complete prompt for the LLM
        """
        return f"""{PromptTemplates.SYSTEM_PROMPT}

{PromptTemplates.REFUSAL_TEMPLATE.format(user_query=user_query)}"""
