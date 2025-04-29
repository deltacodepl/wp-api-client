"""
Settings endpoint for the WordPress REST API
"""

from typing import Dict, Any, Optional
from .base import BaseEndpoint


class Settings(BaseEndpoint):
    """WordPress Settings API wrapper"""
    
    endpoint = "settings"
    
    def get(self, **params) -> Dict[str, Any]:
        """
        Get all settings
        
        Args:
            **params: Query parameters to include in the request
            
        Returns:
            Dictionary of settings
        """
        try:
            return self.client.get(self.endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve settings: {str(e)}") from e
    
    def update(self, **settings) -> Dict[str, Any]:
        """
        Update settings
        
        Args:
            **settings: Settings to update as keyword arguments
            
        Returns:
            Updated settings
        """
        try:
            return self.client.post(self.endpoint, settings)
        except Exception as e:
            raise ValueError(f"Failed to update settings: {str(e)}") from e