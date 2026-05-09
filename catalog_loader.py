"""
Catalog Loader for SHL Assessment Recommender System.

This module handles loading and managing the SHL assessment catalog from JSON file.
It provides functions to load the catalog and access assessments.
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from models import CatalogItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CatalogLoader:
    """
    Handles loading and providing access to the SHL assessment catalog.
    
    This class loads assessments from a JSON file and provides methods
    to access the catalog data throughout the application.
    """
    
    def __init__(self, catalog_path: str = "data/shl_catalog.json"):
        """
        Initialize the catalog loader.
        
        Args:
            catalog_path: Path to the SHL catalog JSON file
        """
        self.catalog_path = Path(catalog_path)
        self._assessments: List[CatalogItem] = []
        self._name_index: Dict[str, CatalogItem] = {}
        self.load_catalog()
    
    def load_catalog(self) -> None:
        """
        Load the SHL catalog from JSON file.
        
        This method reads the catalog file and creates CatalogItem objects.
        It also builds an index for quick lookup by name.
        """
        try:
            if not self.catalog_path.exists():
                logger.warning(f"Catalog file not found at {self.catalog_path}")
                self._assessments = []
                return
            
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(catalog_data, list):
                assessments_data = catalog_data
            elif isinstance(catalog_data, dict) and 'assessments' in catalog_data:
                assessments_data = catalog_data['assessments']
            else:
                logger.error("Invalid catalog format: expected list or dict with 'assessments' key")
                self._assessments = []
                return
            
            # Convert to CatalogItem objects
            self._assessments = []
            self._name_index = {}
            
            for item in assessments_data:
                try:
                    catalog_item = CatalogItem(**item)
                    self._assessments.append(catalog_item)
                    self._name_index[catalog_item.name.lower()] = catalog_item
                except Exception as e:
                    logger.warning(f"Failed to load catalog item: {item}. Error: {e}")
            
            logger.info(f"Loaded {len(self._assessments)} assessments from catalog")
            
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            self._assessments = []
            self._name_index = {}
    
    def get_all_assessments(self) -> List[CatalogItem]:
        """
        Get all assessments from the catalog.
        
        Returns:
            List of all CatalogItem objects
        """
        return self._assessments.copy()
    
    def get_assessment_by_name(self, name: str) -> CatalogItem:
        """
        Get an assessment by name (case-insensitive).
        
        Args:
            name: Name of the assessment to find
            
        Returns:
            CatalogItem if found, None otherwise
        """
        return self._name_index.get(name.lower())
    
    def search_assessments_by_name(self, query: str) -> List[CatalogItem]:
        """
        Search assessments by name (case-insensitive partial match).
        
        Args:
            query: Search query for assessment names
            
        Returns:
            List of matching CatalogItem objects
        """
        query_lower = query.lower()
        return [
            assessment for assessment in self._assessments
            if query_lower in assessment.name.lower()
        ]
    
    def get_assessment_texts(self) -> List[str]:
        """
        Get combined text representation of all assessments for embedding.
        
        Returns:
            List of text strings, one per assessment
        """
        texts = []
        for assessment in self._assessments:
            # Combine relevant fields for semantic search
            text_parts = [
                assessment.name,
                assessment.description,
                assessment.test_type
            ]
            if assessment.duration:
                text_parts.append(f"Duration: {assessment.duration}")
            if assessment.remote_testing:
                text_parts.append("Remote testing available")
            
            texts.append(" | ".join(text_parts))
        
        return texts
    
    def is_empty(self) -> bool:
        """
        Check if the catalog is empty.
        
        Returns:
            True if no assessments are loaded
        """
        return len(self._assessments) == 0


# Global catalog instance
_catalog_loader = None


def get_catalog_loader() -> CatalogLoader:
    """
    Get the global catalog loader instance.
    
    Returns:
        CatalogLoader instance
    """
    global _catalog_loader
    if _catalog_loader is None:
        _catalog_loader = CatalogLoader()
    return _catalog_loader


def reload_catalog() -> None:
    """
    Reload the catalog from file.
    
    This is useful for updating the catalog without restarting the application.
    """
    global _catalog_loader
    if _catalog_loader is not None:
        _catalog_loader.load_catalog()
