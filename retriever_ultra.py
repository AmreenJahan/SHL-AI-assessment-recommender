"""
Ultra-lightweight retriever for memory-constrained environments.

Uses keyword matching instead of FAISS to stay under 512MB.
"""

import logging
from typing import List, Tuple

from embedder_ultra import get_ultra_embedder
from catalog_loader import get_catalog_loader
from models import CatalogItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltraLightRetriever:
    """
    Ultra-lightweight assessment retriever using keyword matching.
    
    Eliminates FAISS and embeddings for minimal memory usage.
    """
    
    def __init__(self):
        """Initialize retriever with keyword matching."""
        self.embedder = get_ultra_embedder()
        self.catalog_loader = get_catalog_loader()
        self.assessments = None
        logger.info("Ultra-lightweight retriever initialized (keyword-based)")
    
    def _load_catalog(self):
        """Load catalog only when needed."""
        if self.assessments is None:
            self.assessments = self.catalog_loader.get_all_assessments()
            logger.info(f"Loaded {len(self.assessments)} assessments")
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[CatalogItem, float]]:
        """
        Search for assessments using keyword matching.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of (assessment, relevance_score) tuples
        """
        self._load_catalog()
        
        # Calculate relevance scores for all assessments
        scored_assessments = []
        
        for assessment in self.assessments:
            # Create search text from assessment
            search_text = f"{assessment.name} {assessment.description} {assessment.test_type}"
            
            # Calculate relevance score
            score = self.embedder.get_relevance_score(query, search_text)
            
            if score > 0.1:  # Only include relevant assessments
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
        
        # Alias matching (for OPQ, GSA, etc.)
        aliases = {
            'opq': 'opq32',
            'gsa': 'g+ general ability test',
            'java': 'java programming test',
            'python': 'python programming test'
        }
        
        if name_lower in aliases:
            alias_target = aliases[name_lower]
            for assessment in self.assessments:
                if alias_target in assessment.name.lower():
                    return assessment
        
        return None


def get_ultra_retriever() -> UltraLightRetriever:
    """Get ultra-lightweight retriever instance."""
    return UltraLightRetriever()
