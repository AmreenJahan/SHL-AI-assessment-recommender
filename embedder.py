"""
Embedder module for SHL Assessment Recommender System.

This module handles text embedding using Sentence Transformers.
It creates vector representations of assessment descriptions and user queries
for semantic similarity matching.
"""

import logging
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextEmbedder:
    """
    Handles text embedding using Sentence Transformers.
    
    This class provides methods to encode text into vector representations
    using the all-MiniLM-L6-v2 model for semantic similarity.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text embedder.
        
        Args:
            model_name: Name of the Sentence Transformer model to use
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Load the Sentence Transformer model.
        
        This method loads the model and caches it for future use.
        """
        try:
            logger.info(f"Loading Sentence Transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        if not texts:
            return np.array([])
        
        try:
            # Encode texts - batch processing for efficiency
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            logger.info(f"Encoded {len(texts)} texts into embeddings of shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise
    
    def encode_single_text(self, text: str) -> np.ndarray:
        """
        Encode a single text into embedding.
        
        Args:
            text: Text string to encode
            
        Returns:
            numpy array of embedding with shape (embedding_dim,)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        if not text.strip():
            raise ValueError("Cannot encode empty text")
        
        try:
            embedding = self.model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            logger.debug(f"Encoded single text into embedding of shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            Integer representing the embedding dimension
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Get embedding dimension by encoding a test text
        test_embedding = self.encode_single_text("test")
        return test_embedding.shape[0]
    
    def is_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self.model is not None


# Global embedder instance
_embedder = None


def get_embedder() -> TextEmbedder:
    """
    Get the global embedder instance.
    
    Returns:
        TextEmbedder instance
    """
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedder()
    return _embedder
