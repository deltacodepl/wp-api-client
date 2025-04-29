"""
Block Patterns endpoint for the WordPress REST API (available in WordPress 5.8+)
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class BlockPatterns(BaseEndpoint):
    """WordPress Block Patterns API wrapper"""
    
    def __init__(self, client):
        """
        Initialize the block patterns endpoint with a client instance
        
        Args:
            client: WordPress API client instance
        """
        super().__init__(client)
        self.endpoint = "__experimental/block-patterns"  # Experimental endpoint as of WP 5.8
    
    def list(self, **params) -> List[Dict]:
        """
        Get all registered block patterns
        
        Args:
            **params: Query parameters to include in the request
            
        Returns:
            List of block patterns
        """
        try:
            return self.client.get(self.endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve block patterns: {str(e)}") from e
    
    def get_categories(self, **params) -> List[Dict]:
        """
        Get all registered block pattern categories
        
        Args:
            **params: Query parameters to include in the request
            
        Returns:
            List of block pattern categories
        """
        try:
            endpoint = "__experimental/block-patterns/categories"
            return self.client.get(endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve block pattern categories: {str(e)}") from e