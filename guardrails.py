"""
Guardrails module for SHL Assessment Recommender System.

This module implements input validation and safety checks to ensure the chatbot
only responds to appropriate SHL-related queries and rejects harmful or irrelevant requests.
"""

import re
import logging
from typing import List, Tuple, Optional

from models import Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Guardrails:
    """
    Implements guardrails to ensure safe and appropriate responses.
    
    This class validates user input to prevent:
    - Non-SHL related queries
    - Legal advice requests
    - General hiring advice outside assessments
    - Prompt injection attempts
    - Harmful or inappropriate content
    """
    
    def __init__(self):
        """Initialize the guardrails with blocked patterns and keywords."""
        # Patterns that should be blocked
        self.blocked_patterns = [
            # Legal advice
            r'.*(legal|lawsuit|sue|court|legal advice|attorney|lawyer).*',
            # General hiring advice (non-assessment related)
            r'.*(how to hire|interview questions|salary negotiation|job offer).*',
            # Prompt injection attempts
            r'.*(ignore previous|forget everything|system prompt|jailbreak|override).*',
            # Harmful content
            r'.*(hack|exploit|vulnerability|malicious|illegal).*',
            # Non-SHL assessment requests
            r'.*(non-SHL|other companies|competitors|alternative assessments).*',
        ]
        
        # SHL-related keywords that indicate valid queries
        self.shl_keywords = [
            'shl', 'assessment', 'test', 'opq', 'gsa', 'personality', 'technical',
            'coding', 'aptitude', 'skills', 'ability', 'behavioral', 'cognitive',
            'java', 'python', 'developer', 'engineer', 'manager', 'analyst',
            'leadership', 'customer service', 'sales', 'remote testing'
        ]
        
        # Clarification indicators (vague queries)
        self.clarification_indicators = [
            'hiring', 'need', 'looking for', 'want', 'require', 'position',
            'role', 'candidate', 'employee', 'team member'
        ]
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a single user message.
        
        Args:
            message: User message to validate
            
        Returns:
            Tuple of (is_valid, rejection_reason_if_invalid)
        """
        message_lower = message.lower().strip()
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.match(pattern, message_lower, re.IGNORECASE):
                logger.warning(f"Blocked message due to pattern: {pattern}")
                return False, self._get_rejection_message(pattern)
        
        # Check if message is completely unrelated to SHL
        if not self._is_shl_related(message_lower):
            logger.warning("Message not related to SHL assessments")
            return False, "I can only help with SHL assessments and tests. Please ask about SHL-specific assessments, tests, or evaluation tools."
        
        return True, None
    
    def validate_conversation(self, messages: List[Message]) -> Tuple[bool, Optional[str]]:
        """
        Validate the entire conversation for safety.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Tuple of (is_valid, rejection_reason_if_invalid)
        """
        if not messages:
            return False, "No messages provided"
        
        # Check each user message
        for message in messages:
            if message.role == "user":
                is_valid, rejection_reason = self.validate_message(message.content)
                if not is_valid:
                    return False, rejection_reason
        
        return True, None
    
    def needs_clarification(self, message: str) -> bool:
        """
        Check if a message needs clarification.
        
        Args:
            message: User message to check
            
        Returns:
            True if clarification is needed, False otherwise
        """
        message_lower = message.lower().strip()
        
        # Check if message contains clarification indicators but lacks specific details
        has_indicator = any(indicator in message_lower for indicator in self.clarification_indicators)
        
        # Check if message is too short or vague
        is_vague = (
            len(message_lower.split()) < 5 or
            message_lower in ['hiring', 'need test', 'looking for assessment'] or
            not any(keyword in message_lower for keyword in self.shl_keywords)
        )
        
        return has_indicator and is_vague
    
    def get_clarification_questions(self, message: str) -> List[str]:
        """
        Generate clarification questions for vague queries.
        
        Args:
            message: User message that needs clarification
            
        Returns:
            List of clarification questions
        """
        questions = []
        message_lower = message.lower()
        
        # Basic clarification questions
        questions.append("What seniority level are you hiring for? (e.g., entry-level, mid-level, senior)")
        questions.append("What type of role is this? (e.g., technical, management, customer-facing)")
        questions.append("Do you need technical skills assessment, personality assessment, or both?")
        questions.append("Is remote testing required?")
        
        # Context-specific questions based on message content
        if 'developer' in message_lower or 'engineer' in message_lower:
            questions.append("What programming languages or technologies are needed?")
        
        if 'manager' in message_lower or 'leadership' in message_lower:
            questions.append("Is this for a people management role or individual contributor?")
        
        if 'customer' in message_lower or 'sales' in message_lower:
            questions.append("Do you need to assess customer service or sales skills?")
        
        return questions[:3]  # Return max 3 questions to avoid overwhelming
    
    def is_comparison_request(self, message: str) -> bool:
        """
        Check if the message is requesting a comparison.
        
        Args:
            message: User message to check
            
        Returns:
            True if it's a comparison request, False otherwise
        """
        comparison_keywords = [
            'compare', 'difference', 'versus', 'vs', 'between', 'better',
            'which one', 'what is the difference', 'comparison'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in comparison_keywords)
    
    def extract_comparison_items(self, message: str) -> List[str]:
        """
        Extract assessment names from a comparison request.
        
        Args:
            message: User message containing comparison request
            
        Returns:
            List of assessment names to compare
        """
        # Simple extraction - look for assessment codes like OPQ, GSA
        assessment_codes = re.findall(r'\b[A-Z]{2,4}\b', message.upper())
        
        # Also look for common assessment names
        common_names = ['personality', 'technical', 'coding', 'aptitude', 'behavioral']
        message_lower = message.lower()
        
        for name in common_names:
            if name in message_lower:
                assessment_codes.append(name.title())
        
        return list(set(assessment_codes))  # Remove duplicates
    
    def _is_shl_related(self, message: str) -> bool:
        """
        Check if a message is related to SHL assessments.
        
        Args:
            message: User message to check
            
        Returns:
            True if SHL-related, False otherwise
        """
        # Check for SHL keywords
        if any(keyword in message for keyword in self.shl_keywords):
            return True
        
        # Check for assessment-related terms
        assessment_terms = ['assessment', 'test', 'evaluation', 'measure', 'screen']
        if any(term in message for term in assessment_terms):
            return True
        
        return False
    
    def _get_rejection_message(self, pattern: str) -> str:
        """
        Get appropriate rejection message based on the blocked pattern.
        
        Args:
            pattern: The pattern that triggered the rejection
            
        Returns:
            Appropriate rejection message
        """
        if 'legal' in pattern:
            return "I cannot provide legal advice. Please consult with a qualified legal professional."
        elif 'how to hire' in pattern or 'interview questions' in pattern:
            return "I can only recommend SHL assessments for candidate evaluation. For general hiring advice, please consult HR resources."
        elif 'ignore' in pattern or 'system prompt' in pattern:
            return "I cannot process that request. Please ask about SHL assessments and tests."
        elif 'hack' in pattern or 'exploit' in pattern:
            return "I cannot assist with harmful or malicious requests."
        else:
            return "I can only help with SHL assessments and tests. Please ask about SHL-specific products or services."


# Global guardrails instance
_guardrails = None


def get_guardrails() -> Guardrails:
    """
    Get the global guardrails instance.
    
    Returns:
        Guardrails instance
    """
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails
