"""
Base class for WordPress REST API endpoints
"""

from typing import Dict, List, Any, Optional, Union


class BaseEndpoint:
    """Base class for WordPress REST API endpoints"""
    
    endpoint = None  # To be defined in subclasses
    
    def __init__(self, client):
        """
        Initialize the endpoint with a client instance
        
        Args:
            client: WordPress API client instance
        """
        self.client = client
        
    def list(self, **params) -> List[Dict]:
        """
        Get a list of items from this endpoint
        
        Args:
            **params: Query parameters to include in the request
            
        Returns:
            List of items
        """
        return self.client.get(self.endpoint, params)
    
    def get(self, id: int, **params) -> Dict:
        """
        Get a single item by ID
        
        Args:
            id: Item ID
            **params: Query parameters to include in the request
            
        Returns:
            Item data
        """
        endpoint = f"{self.endpoint}/{id}"
        return self.client.get(endpoint, params)
    
    def create(self, data: Dict) -> Dict:
        """
        Create a new item
        
        Args:
            data: Item data
            
        Returns:
            Created item data
        """
        return self.client.post(self.endpoint, data)
    
    def update(self, id: int, data: Dict) -> Dict:
        """
        Update an existing item
        
        Args:
            id: Item ID
            data: Item data to update
            
        Returns:
            Updated item data
        """
        endpoint = f"{self.endpoint}/{id}"
        return self.client.put(endpoint, data)
    
    def delete(self, id: int, **params) -> Dict:
        """
        Delete an item
        
        Args:
            id: Item ID
            **params: Query parameters to include in the request
            
        Returns:
            Deleted item data
        """
        endpoint = f"{self.endpoint}/{id}"
        return self.client.delete(endpoint, params)