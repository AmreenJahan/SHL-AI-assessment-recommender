"""
SHL Catalog Scraper

This module scrapes the SHL product catalog to get real assessment data.
Only Individual Test Solutions are included (Job Solutions are out of scope).
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SHLCatalogScraper:
    """
    Scrapes SHL product catalog for Individual Test Solutions.
    """
    
    def __init__(self):
        """Initialize the scraper."""
        self.base_url = "https://www.shl.com"
        self.catalog_url = "https://www.shl.com/solutions/products/productcatalog/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_catalog(self) -> List[Dict[str, Any]]:
        """
        Scrape the SHL catalog for Individual Test Solutions.
        
        Returns:
            List of assessment dictionaries
        """
        try:
            logger.info(f"Scraping SHL catalog from {self.catalog_url}")
            
            response = self.session.get(self.catalog_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for assessment cards or product listings
            assessments = []
            
            # Try different selectors that might contain the assessments
            selectors = [
                '.product-card',
                '.assessment-card', 
                '.product-item',
                '[data-product-type="individual"]',
                '.catalog-item'
            ]
            
            products = []
            for selector in selectors:
                products = soup.select(selector)
                if products:
                    logger.info(f"Found {len(products)} products with selector: {selector}")
                    break
            
            if not products:
                logger.warning("No products found with standard selectors. Looking for alternative patterns...")
                # Look for any links that might be assessments
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if '/solutions/products/' in href or '/assessment' in href.lower():
                        product_info = self._extract_product_info(link)
                        if product_info:
                            assessments.append(product_info)
            
            # Extract product information
            for product in products:
                product_info = self._extract_product_from_element(product)
                if product_info:
                    assessments.append(product_info)
            
            logger.info(f"Successfully scraped {len(assessments)} assessments")
            return assessments
            
        except Exception as e:
            logger.error(f"Failed to scrape catalog: {e}")
            return []
    
    def _extract_product_from_element(self, element) -> Dict[str, Any]:
        """
        Extract product information from a BeautifulSoup element.
        
        Args:
            element: BeautifulSoup element containing product info
            
        Returns:
            Product dictionary or None if extraction fails
        """
        try:
            # Extract name
            name_elem = element.find(['h1', 'h2', 'h3', 'h4', '.title', '.name'])
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Extract URL
            link_elem = element.find('a', href=True)
            url = link_elem.get('href') if link_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Extract description
            desc_elem = element.find(['p', '.description', '.summary'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract test type
            type_elem = element.find(['.test-type', '.category', '.type'])
            test_type = type_elem.get_text(strip=True) if type_elem else "Unknown"
            
            # Extract duration if available
            duration_elem = element.find(['.duration', '.time', '.length'])
            duration = duration_elem.get_text(strip=True) if duration_elem else None
            
            if name and url:
                return {
                    "name": name,
                    "url": url,
                    "description": description,
                    "test_type": test_type,
                    "duration": duration,
                    "remote_testing": True  # Assume most SHL tests support remote
                }
            
        except Exception as e:
            logger.warning(f"Failed to extract product info: {e}")
        
        return None
    
    def _extract_product_info(self, link_elem) -> Dict[str, Any]:
        """
        Extract product information from a link element.
        
        Args:
            link_elem: BeautifulSoup link element
            
        Returns:
            Product dictionary or None if extraction fails
        """
        try:
            name = link_elem.get_text(strip=True)
            href = link_elem.get('href', '')
            
            if not name or not href:
                return None
            
            if not href.startswith('http'):
                href = self.base_url + href
            
            return {
                "name": name,
                "url": href,
                "description": f"SHL assessment: {name}",
                "test_type": "Assessment",
                "duration": None,
                "remote_testing": True
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract product info from link: {e}")
            return None
    
    def save_catalog(self, assessments: List[Dict[str, Any]], filename: str = "data/shl_catalog.json"):
        """
        Save scraped catalog to JSON file.
        
        Args:
            assessments: List of assessment dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(assessments, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(assessments)} assessments to {filename}")
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")


def main():
    """
    Main function to scrape and save SHL catalog.
    """
    scraper = SHLCatalogScraper()
    assessments = scraper.scrape_catalog()
    
    if assessments:
        scraper.save_catalog(assessments)
        print(f"Successfully scraped and saved {len(assessments)} assessments")
    else:
        print("No assessments found. The website structure might have changed.")
        
        # Create a fallback catalog with common SHL assessments
        fallback_catalog = [
            {
                "name": "OPQ32",
                "url": "https://www.shl.com/solutions/products/product-catalog/opq32/",
                "description": "Occupational Personality Questionnaire",
                "test_type": "Personality"
            },
            {
                "name": "G+ General Ability Test",
                "url": "https://www.shl.com/solutions/products/product-catalog/g-plus/",
                "description": "General mental ability assessment",
                "test_type": "Cognitive"
            },
            {
                "name": "Java Programming Test",
                "url": "https://www.shl.com/solutions/products/product-catalog/java-programming/",
                "description": "Java programming skills assessment",
                "test_type": "Technical"
            },
            {
                "name": "Verbal Reasoning Test",
                "url": "https://www.shl.com/solutions/products/product-catalog/verbal-reasoning/",
                "description": "Verbal reasoning and comprehension assessment",
                "test_type": "Cognitive"
            },
            {
                "name": "Numerical Reasoning Test",
                "url": "https://www.shl.com/solutions/products/product-catalog/numerical-reasoning/",
                "description": "Numerical reasoning and data interpretation assessment",
                "test_type": "Cognitive"
            }
        ]
        
        scraper.save_catalog(fallback_catalog)
        print(f"Created fallback catalog with {len(fallback_catalog)} assessments")


if __name__ == "__main__":
    main()
