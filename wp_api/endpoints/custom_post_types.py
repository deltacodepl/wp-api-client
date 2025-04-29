"""
Custom Post Types support for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class CustomPostType(BaseEndpoint):
    """WordPress Custom Post Type API wrapper"""
    
    def __init__(self, client, post_type: str):
        """
        Initialize the custom post type endpoint with a client instance
        
        Args:
            client: WordPress API client instance
            post_type: Custom post type slug (e.g., 'product', 'portfolio', etc.)
        """
        super().__init__(client)
        self.post_type = post_type
        self.endpoint = post_type
    
    def list(
        self,
        context: str = "view",
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        after: str = None,
        author: Union[int, List[int]] = None,
        author_exclude: Union[int, List[int]] = None,
        before: str = None,
        exclude: Union[int, List[int]] = None,
        include: Union[int, List[int]] = None,
        offset: int = None,
        order: str = "desc",
        orderby: str = "date",
        slug: Union[str, List[str]] = None,
        status: Union[str, List[str]] = "publish",
        **kwargs
    ) -> List[Dict]:
        """
        List custom post type items with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            after: Limit response to posts published after a given ISO8601 compliant date
            author: Limit result set to posts assigned to specific authors
            author_exclude: Ensure result set excludes posts assigned to specific authors
            before: Limit response to posts published before a given ISO8601 compliant date
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            offset: Offset the result set by a specific number of items
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (date, author, title, etc.)
            slug: Limit result set to posts with one or more specific slugs
            status: Limit result set to posts with specific statuses
            
        Returns:
            List of custom post type items
        """
        try:
            params = {
                "context": context,
                "page": page,
                "per_page": per_page,
                "order": order,
                "orderby": orderby,
            }
            
            # Add optional parameters
            if search:
                params["search"] = search
            if after:
                params["after"] = after
            if author:
                params["author"] = author if isinstance(author, int) else ",".join(map(str, author))
            if author_exclude:
                params["author_exclude"] = author_exclude if isinstance(author_exclude, int) else ",".join(map(str, author_exclude))
            if before:
                params["before"] = before
            if exclude:
                params["exclude"] = exclude if isinstance(exclude, int) else ",".join(map(str, exclude))
            if include:
                params["include"] = include if isinstance(include, int) else ",".join(map(str, include))
            if offset:
                params["offset"] = offset
            if slug:
                params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
            if status:
                params["status"] = status if isinstance(status, str) else ",".join(status)
                
            # Add any additional parameters
            params.update(kwargs)
            
            return self.client.get(self.endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to list {self.post_type} items: {str(e)}") from e
    
    def get(self, id: int, **params) -> Dict:
        """
        Get a single custom post type item by ID
        
        Args:
            id: Item ID
            **params: Query parameters to include in the request
            
        Returns:
            Custom post type item data
        """
        try:
            endpoint = f"{self.endpoint}/{id}"
            return self.client.get(endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to get {self.post_type} item with ID {id}: {str(e)}") from e
    
    def create(self, title: str, content: str = None, status: str = "publish", **kwargs) -> Dict:
        """
        Create a new custom post type item
        
        Args:
            title: Item title
            content: Item content
            status: Item status (publish, future, draft, pending, private)
            **kwargs: Additional item data
            
        Returns:
            Created custom post type item data
        """
        try:
            data = {"title": title}
            
            if content is not None:
                data["content"] = content
            if status is not None:
                data["status"] = status
                
            # Add any additional data
            data.update(kwargs)
            
            return self.client.post(self.endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to create {self.post_type} item: {str(e)}") from e
    
    def update(self, id: int, title: str = None, content: str = None, status: str = None, **kwargs) -> Dict:
        """
        Update an existing custom post type item
        
        Args:
            id: Item ID
            title: Item title
            content: Item content
            status: Item status (publish, future, draft, pending, private)
            **kwargs: Additional item data to update
            
        Returns:
            Updated custom post type item data
        """
        try:
            data = {}
            
            if title is not None:
                data["title"] = title
            if content is not None:
                data["content"] = content
            if status is not None:
                data["status"] = status
                
            # Add any additional data
            data.update(kwargs)
            
            endpoint = f"{self.endpoint}/{id}"
            return self.client.put(endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to update {self.post_type} item with ID {id}: {str(e)}") from e
    
    def delete(self, id: int, force: bool = False) -> Dict:
        """
        Delete a custom post type item
        
        Args:
            id: Item ID
            force: Whether to bypass the trash and force deletion
            
        Returns:
            Deleted custom post type item data
        """
        try:
            endpoint = f"{self.endpoint}/{id}"
            return self.client.delete(endpoint, {"force": "true" if force else "false"})
        except Exception as e:
            raise ValueError(f"Failed to delete {self.post_type} item with ID {id}: {str(e)}") from e
    
    def get_meta(self):
        """
        Get a custom fields handler for this custom post type
        
        Returns:
            CustomFields endpoint handler for this custom post type
        """
        from .custom_fields import CustomFields
        return CustomFields(self.client, self.post_type)