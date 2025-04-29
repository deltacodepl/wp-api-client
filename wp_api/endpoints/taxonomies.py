"""
Taxonomies endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Taxonomies(BaseEndpoint):
    """WordPress Taxonomies API wrapper"""
    
    endpoint = "taxonomies"
    
    def list(self, **params) -> Dict[str, Dict]:
        """
        Get all registered taxonomies
        
        Args:
            **params: Query parameters to include in the request
            
        Returns:
            Dictionary of taxonomies
        """
        try:
            return self.client.get(self.endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve taxonomies: {str(e)}") from e
    
    def get(self, taxonomy: str, **params) -> Dict:
        """
        Get a specific taxonomy
        
        Args:
            taxonomy: Taxonomy slug (e.g., 'category', 'post_tag')
            **params: Query parameters to include in the request
            
        Returns:
            Taxonomy data
        """
        try:
            endpoint = f"{self.endpoint}/{taxonomy}"
            return self.client.get(endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve taxonomy '{taxonomy}': {str(e)}") from e


class Terms(BaseEndpoint):
    """Base class for taxonomy terms endpoints"""
    
    def __init__(self, client, taxonomy: str):
        """
        Initialize the terms endpoint with a client instance and taxonomy
        
        Args:
            client: WordPress API client instance
            taxonomy: Taxonomy slug (e.g., 'category', 'post_tag')
        """
        super().__init__(client)
        self.taxonomy = taxonomy
        self.endpoint = f"{taxonomy}"
    
    def list(
        self,
        context: str = "view",
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        exclude: Union[int, List[int]] = None,
        include: Union[int, List[int]] = None,
        order: str = "asc",
        orderby: str = "name",
        hide_empty: bool = False,
        parent: int = None,
        post: int = None,
        slug: Union[str, List[str]] = None,
        **kwargs
    ) -> List[Dict]:
        """
        List taxonomy terms with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (id, name, slug, etc.)
            hide_empty: Whether to hide terms that don't have any posts
            parent: Limit result set to terms that have a specific parent ID
            post: Limit result set to terms assigned to a specific post
            slug: Limit result set to terms with one or more specific slugs
            
        Returns:
            List of terms
        """
        try:
            params = {
                "context": context,
                "page": page,
                "per_page": per_page,
                "order": order,
                "orderby": orderby,
                "hide_empty": "true" if hide_empty else "false",
            }
            
            # Add optional parameters
            if search:
                params["search"] = search
            if exclude:
                params["exclude"] = exclude if isinstance(exclude, int) else ",".join(map(str, exclude))
            if include:
                params["include"] = include if isinstance(include, int) else ",".join(map(str, include))
            if parent is not None:
                params["parent"] = parent
            if post:
                params["post"] = post
            if slug:
                params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
                
            # Add any additional parameters
            params.update(kwargs)
            
            return self.client.get(self.endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve terms for taxonomy '{self.taxonomy}': {str(e)}") from e
    
    def get(self, id: int, **params) -> Dict:
        """
        Get a specific term
        
        Args:
            id: Term ID
            **params: Query parameters to include in the request
            
        Returns:
            Term data
        """
        try:
            endpoint = f"{self.endpoint}/{id}"
            return self.client.get(endpoint, params)
        except Exception as e:
            raise ValueError(f"Failed to retrieve term '{id}' for taxonomy '{self.taxonomy}': {str(e)}") from e
    
    def create(
        self,
        name: str,
        slug: str = None,
        description: str = None,
        parent: int = None,
        meta: Dict = None,
        **kwargs
    ) -> Dict:
        """
        Create a new term
        
        Args:
            name: Term name
            slug: Term slug
            description: Term description
            parent: Parent term ID
            meta: Term meta data
            
        Returns:
            Created term data
        """
        try:
            data = {"name": name}
            
            if slug is not None:
                data["slug"] = slug
            if description is not None:
                data["description"] = description
            if parent is not None:
                data["parent"] = parent
            if meta is not None:
                data["meta"] = meta
                
            # Add any additional data
            data.update(kwargs)
            
            return self.client.post(self.endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to create term for taxonomy '{self.taxonomy}': {str(e)}") from e
    
    def update(
        self,
        id: int,
        name: str = None,
        slug: str = None,
        description: str = None,
        parent: int = None,
        meta: Dict = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing term
        
        Args:
            id: Term ID
            name: Term name
            slug: Term slug
            description: Term description
            parent: Parent term ID
            meta: Term meta data
            
        Returns:
            Updated term data
        """
        try:
            data = {}
            
            if name is not None:
                data["name"] = name
            if slug is not None:
                data["slug"] = slug
            if description is not None:
                data["description"] = description
            if parent is not None:
                data["parent"] = parent
            if meta is not None:
                data["meta"] = meta
                
            # Add any additional data
            data.update(kwargs)
            
            endpoint = f"{self.endpoint}/{id}"
            return self.client.put(endpoint, data)
        except Exception as e:
            raise ValueError(f"Failed to update term '{id}' for taxonomy '{self.taxonomy}': {str(e)}") from e
    
    def delete(self, id: int, force: bool = False) -> Dict:
        """
        Delete a term
        
        Args:
            id: Term ID
            force: Whether to bypass the trash and force deletion
            
        Returns:
            Deleted term data
        """
        try:
            endpoint = f"{self.endpoint}/{id}"
            return self.client.delete(endpoint, {"force": "true" if force else "false"})
        except Exception as e:
            raise ValueError(f"Failed to delete term '{id}' for taxonomy '{self.taxonomy}': {str(e)}") from e