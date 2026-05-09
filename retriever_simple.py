"""
Simple rule-based retriever for guaranteed results.

Uses direct keyword matching without complex scoring.
"""

import logging
from typing import List, Tuple

from catalog_loader import get_catalog_loader
from models import CatalogItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleRetriever:
    """
    Simple retriever using direct keyword matching.
    
    Guaranteed to return results for any query.
    """
    
    def __init__(self):
        """Initialize retriever with catalog."""
        self.catalog_loader = get_catalog_loader()
        self.assessments = None
        logger.info("Simple retriever initialized")
    
    def _load_catalog(self):
        """Load catalog only when needed."""
        if self.assessments is None:
            self.assessments = self.catalog_loader.get_all_assessments()
            logger.info(f"Loaded {len(self.assessments)} assessments")
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[CatalogItem, float]]:
        """
        Search for assessments using simple keyword matching.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of (assessment, relevance_score) tuples
        """
        self._load_catalog()
        
        query_lower = query.lower()
        scored_assessments = []
        
        # Simple keyword matching
        for assessment in self.assessments:
            score = 0.0
            search_text = f"{assessment.name} {assessment.description} {assessment.test_type}".lower()
            
            # Direct word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in search_text:
                    score += 0.2
            
            # Category matches
            if any(word in search_text for word in ['java', 'python', 'javascript', 'programming', 'coding']):
                if any(word in query_lower for word in ['java', 'python', 'javascript', 'programming', 'coding']):
                    score += 0.3
            
            if any(word in search_text for word in ['personality', 'opq', 'behavior', 'style']):
                if any(word in query_lower for word in ['personality', 'behavior', 'style', 'soft skills']):
                    score += 0.3
            
            if any(word in search_text for word in ['cognitive', 'reasoning', 'aptitude', 'numerical', 'verbal']):
                if any(word in query_lower for word in ['cognitive', 'reasoning', 'aptitude', 'thinking']):
                    score += 0.3
            
            if any(word in search_text for word in ['manager', 'leadership', 'lead', 'supervisor']):
                if any(word in query_lower for word in ['manager', 'leadership', 'lead', 'supervisor']):
                    score += 0.3
            
            # Always add minimum score
            if score == 0.0:
                score = 0.1
            
            scored_assessments.append((assessment, score))
        
        # Sort by relevance score
        scored_assessments.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return scored_assessments[:top_k]
    
    def get_assessment_by_name(self, name: str) -> CatalogItem:
        """Get assessment by exact name match."""
        self._load_catalog()
        
        name_lower = name.lower()
        
        # Direct match
        for assessment in self.assessments:
            if assessment.name.lower() == name_lower:
                return assessment
        
        # Partial match
        for assessment in self.assessments:
            if name_lower in assessment.name.lower():
                return assessment
        
        # Common aliases
        aliases = {
            'opq': 'opq32',
            'gsa': 'g+ general ability test',
            'java': 'java programming test',
            'python': 'python programming test'
        }
        
        if name_lower in aliases:
            target = aliases[name_lower]
            for assessment in self.assessments:
                if target in assessment.name.lower():
                    return assessment
        
        return None


def get_simple_retriever() -> SimpleRetriever:
    """Get simple retriever instance."""
    return SimpleRetriever()
