"""
Custom fields (post meta) endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class CustomFields(BaseEndpoint):
    """WordPress Custom Fields (post meta) API wrapper"""
    
    def __init__(self, client, post_type: str = "posts"):
        """
        Initialize the custom fields endpoint with a client instance and post type
        
        Args:
            client: WordPress API client instance
            post_type: Post type (posts, pages, or custom post type)
        """
        super().__init__(client)
        self.post_type = post_type
        self.endpoint = f"{post_type}"
    
    def get_all(self, post_id: int, **params) -> Dict:
        """
        Get all custom fields (meta) for a post
        
        Args:
            post_id: Post ID
            **params: Query parameters to include in the request
            
        Returns:
            Post meta data
        """
        try:
            endpoint = f"{self.endpoint}/{post_id}"
            post_data = self.client.get(endpoint, params)
            return post_data.get("meta", {})
        except Exception as e:
            raise ValueError(f"Failed to retrieve meta for {self.post_type} ID {post_id}: {str(e)}") from e
    
    def get(self, post_id: int, meta_key: str, **params) -> Any:
        """
        Get a specific custom field (meta) for a post
        
        Args:
            post_id: Post ID
            meta_key: Meta key
            **params: Query parameters to include in the request
            
        Returns:
            Meta value
        """
        try:
            endpoint = f"{self.endpoint}/{post_id}/meta"
            meta_items = self.client.get(endpoint, params)
            
            for item in meta_items:
                if item.get("key") == meta_key:
                    return item.get("value")
                    
            return None
        except Exception as e:
            raise ValueError(f"Failed to retrieve meta key '{meta_key}' for {self.post_type} ID {post_id}: {str(e)}") from e
    
    def create(self, post_id: int, meta_key: str, meta_value: Any) -> Dict:
        """
        Create a new custom field (meta) for a post
        
        Args:
            post_id: Post ID
            meta_key: Meta key
            meta_value: Meta value
            
        Returns:
            Created meta data
        """
        try:
            endpoint = f"{self.endpoint}/{post_id}/meta"
            data = {
                "key": meta_key,
                "value": meta_value
            }
            return self.client.post(endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to create meta key '{meta_key}' for {self.post_type} ID {post_id}: {str(e)}") from e
    
    def update(self, post_id: int, meta_id: int, meta_value: Any) -> Dict:
        """
        Update an existing custom field (meta) for a post
        
        Args:
            post_id: Post ID
            meta_id: Meta ID
            meta_value: New meta value
            
        Returns:
            Updated meta data
        """
        try:
            endpoint = f"{self.endpoint}/{post_id}/meta/{meta_id}"
            data = {
                "value": meta_value
            }
            return self.client.put(endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to update meta ID {meta_id} for {self.post_type} ID {post_id}: {str(e)}") from e
    
    def delete(self, post_id: int, meta_id: int, force: bool = True) -> Dict:
        """
        Delete a custom field (meta) for a post
        
        Args:
            post_id: Post ID
            meta_id: Meta ID
            force: Whether to bypass the trash and force deletion
            
        Returns:
            Deleted meta data
        """
        try:
            endpoint = f"{self.endpoint}/{post_id}/meta/{meta_id}"
            return self.client.delete(endpoint, {"force": "true" if force else "false"})
        except Exception as e:
            raise ValueError(f"Failed to delete meta ID {meta_id} for {self.post_type} ID {post_id}: {str(e)}") from e
    
    def update_or_create(self, post_id: int, meta_key: str, meta_value: Any) -> Dict:
        """
        Update an existing custom field or create if it doesn't exist
        
        Args:
            post_id: Post ID
            meta_key: Meta key
            meta_value: Meta value
            
        Returns:
            Updated or created meta data
        """
        try:
            # Get all meta for the post
            endpoint = f"{self.endpoint}/{post_id}/meta"
            meta_items = self.client.get(endpoint)
            
            # Check if meta key already exists
            for item in meta_items:
                if item.get("key") == meta_key:
                    # Update existing meta
                    meta_id = item.get("id")
                    return self.update(post_id, meta_id, meta_value)
            
            # Create new meta
            return self.create(post_id, meta_key, meta_value)
        except Exception as e:
            raise ValueError(f"Failed to update or create meta key '{meta_key}' for {self.post_type} ID {post_id}: {str(e)}") from e