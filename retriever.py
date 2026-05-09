"""
FAISS Retriever for SHL Assessment Recommender System.

This module handles semantic similarity search using FAISS (Facebook AI Similarity Search).
It provides fast retrieval of relevant assessments based on user queries.
"""

import logging
import numpy as np
from typing import List, Tuple, Optional
import faiss

from embedder import get_embedder
from catalog_loader import get_catalog_loader
from models import CatalogItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssessmentRetriever:
    """
    Handles semantic retrieval of SHL assessments using FAISS.
    
    This class builds and maintains a FAISS index for fast similarity search
    between user queries and assessment descriptions.
    """
    
    def __init__(self):
        """
        Initialize the assessment retriever.
        
        This loads the catalog, embedder, and builds the FAISS index.
        """
        self.catalog_loader = get_catalog_loader()
        self.embedder = get_embedder()
        self.index: Optional[faiss.IndexFlatL2] = None
        self.assessment_texts: List[str] = []
        self.assessment_items: List[CatalogItem] = []
        self._build_index()
    
    def _build_index(self) -> None:
        """
        Build the FAISS index from the catalog.
        
        This method creates embeddings for all assessments and builds
        a FAISS index for fast similarity search.
        """
        try:
            # Get all assessments from catalog
            self.assessment_items = self.catalog_loader.get_all_assessments()
            
            if not self.assessment_items:
                logger.warning("No assessments found in catalog")
                return
            
            # Get text representations for embedding
            self.assessment_texts = self.catalog_loader.get_assessment_texts()
            
            # Create embeddings
            embeddings = self.embedder.encode_texts(self.assessment_texts)
            
            if embeddings.size == 0:
                logger.error("Failed to create embeddings")
                return
            
            # Build FAISS index
            embedding_dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(embedding_dim)
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {self.index.ntotal} assessments")
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[CatalogItem, float]]:
        """
        Search for relevant assessments based on query.
        
        Args:
            query: User query string
            top_k: Number of top results to return
            
        Returns:
            List of tuples containing (CatalogItem, similarity_score)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index not built or empty")
            return []
        
        try:
            # Encode the query
            query_embedding = self.embedder.encode_single_text(query)
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Convert results to assessment items with scores
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx >= 0 and idx < len(self.assessment_items):
                    assessment = self.assessment_items[idx]
                    # Convert distance to similarity score (lower distance = higher similarity)
                    similarity_score = 1.0 / (1.0 + distance)
                    results.append((assessment, similarity_score))
            
            logger.info(f"Found {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
    
    def get_assessment_by_name(self, name: str) -> Optional[CatalogItem]:
        """
        Get a specific assessment by name.
        
        Args:
            name: Name of the assessment
            
        Returns:
            CatalogItem if found, None otherwise
        """
        return self.catalog_loader.get_assessment_by_name(name)
    
    def search_assessments_by_name(self, query: str) -> List[CatalogItem]:
        """
        Search assessments by name (exact/partial match).
        
        Args:
            query: Search query for assessment names
            
        Returns:
            List of matching CatalogItem objects
        """
        return self.catalog_loader.search_assessments_by_name(query)
    
    def is_ready(self) -> bool:
        """
        Check if the retriever is ready for search.
        
        Returns:
            True if index is built and ready, False otherwise
        """
        return self.index is not None and self.index.ntotal > 0
    
    def get_index_stats(self) -> dict:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {"status": "not_built"}
        
        return {
            "status": "ready",
            "total_assessments": self.index.ntotal,
            "embedding_dimension": self.index.d if hasattr(self.index, 'd') else "unknown"
        }


# Global retriever instance
_retriever = None


def get_retriever() -> AssessmentRetriever:
    """
    Get the global retriever instance.
    
    Returns:
        AssessmentRetriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = AssessmentRetriever()
    return _retriever


def rebuild_index() -> None:
    """
    Rebuild the search index.
    
    This is useful when the catalog is updated.
    """
    global _retriever
    if _retriever is not None:
        _retriever._build_index()
