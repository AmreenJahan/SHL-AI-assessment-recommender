"""
Ultra-lightweight embedder for memory-constrained environments.

Uses minimal model and on-demand loading to stay under 512MB.
"""

import logging
import re
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltraLightEmbedder:
    """
    Ultra-lightweight text embedder using keyword matching.
    
    Eliminates ML models entirely for minimal memory usage.
    """
    
    def __init__(self):
        """Initialize with keyword-based matching."""
        logger.info("Ultra-lightweight embedder initialized (keyword-based)")
        
        # Technical keywords for matching
        self.tech_keywords = {
            'java': ['java', 'jvm', 'spring', 'maven', 'gradle'],
            'python': ['python', 'django', 'flask', 'numpy', 'pandas'],
            'javascript': ['javascript', 'js', 'node', 'react', 'angular', 'vue'],
            'database': ['sql', 'database', 'mysql', 'postgresql', 'oracle'],
            'web': ['web', 'html', 'css', 'frontend', 'backend'],
            'mobile': ['mobile', 'ios', 'android', 'swift', 'kotlin'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws'],
            'testing': ['testing', 'qa', 'unit', 'integration', 'automation']
        }
        
        # Role keywords for matching
        self.role_keywords = {
            'developer': ['developer', 'programmer', 'engineer', 'coder'],
            'manager': ['manager', 'lead', 'supervisor', 'team lead'],
            'analyst': ['analyst', 'business analyst', 'data analyst'],
            'consultant': ['consultant', 'advisor', 'specialist'],
            'graduate': ['graduate', 'entry', 'junior', 'trainee'],
            'senior': ['senior', 'experienced', 'lead', 'principal']
        }
        
        # Assessment keywords for matching
        self.assessment_keywords = {
            'cognitive': ['reasoning', 'aptitude', 'verbal', 'numerical', 'abstract'],
            'personality': ['personality', 'behavior', 'style', 'opq', 'motivation'],
            'technical': ['technical', 'programming', 'coding', 'java', 'python'],
            'skills': ['skills', 'competency', 'ability', 'capability']
        }
    
    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Encode texts using keyword matching (returns dummy embeddings).
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            List of dummy embeddings (for compatibility)
        """
        # Return simple embeddings based on keyword presence
        embeddings = []
        for text in texts:
            text_lower = text.lower()
            embedding = self._create_keyword_embedding(text_lower)
            embeddings.append(embedding)
        
        return embeddings
    
    def _create_keyword_embedding(self, text: str) -> List[float]:
        """Create embedding based on keyword presence."""
        embedding = [0.0] * 20  # Small fixed-size embedding
        
        # Technical keywords (indices 0-9)
        for i, (category, keywords) in enumerate(self.tech_keywords.items()):
            if any(keyword in text for keyword in keywords):
                embedding[i] = 1.0
        
        # Role keywords (indices 10-15)
        for i, (category, keywords) in enumerate(self.role_keywords.items()):
            if any(keyword in text for keyword in keywords):
                embedding[10 + i] = 1.0
        
        # Assessment keywords (indices 16-19)
        for i, (category, keywords) in enumerate(self.assessment_keywords.items()):
            if any(keyword in text for keyword in keywords):
                embedding[16 + i] = 1.0
        
        return embedding
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return 20  # Small fixed dimension
    
    def get_relevance_score(self, query: str, assessment_text: str) -> float:
        """
        Calculate relevance score between query and assessment.
        
        Args:
            query: User query
            assessment_text: Assessment description
            
        Returns:
            Relevance score between 0 and 1
        """
        query_lower = query.lower()
        text_lower = assessment_text.lower()
        
        score = 0.0
        
        # Exact word matches
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        
        # Calculate overlap ratio
        if query_words:
            overlap = len(query_words.intersection(text_words))
            score += overlap / len(query_words) * 0.5
        
        # Keyword category matches
        for category, keywords in self.tech_keywords.items():
            query_has = any(kw in query_lower for kw in keywords)
            text_has = any(kw in text_lower for kw in keywords)
            if query_has and text_has:
                score += 0.1
        
        for category, keywords in self.assessment_keywords.items():
            query_has = any(kw in query_lower for kw in keywords)
            text_has = any(kw in text_lower for kw in keywords)
            if query_has and text_has:
                score += 0.1
        
        return min(score + 0.4, 1.0)  # Higher base score to ensure results


def get_ultra_embedder() -> UltraLightEmbedder:
    """Get ultra-lightweight embedder instance."""
    return UltraLightEmbedder()
