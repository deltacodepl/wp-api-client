"""
Categories endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Categories(BaseEndpoint):
    """WordPress Categories API wrapper"""
    
    endpoint = "categories"
    
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
        List categories with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (id, name, slug, etc.)
            hide_empty: Whether to hide categories that don't have any posts
            parent: Limit result set to categories that have a specific parent ID
            post: Limit result set to categories assigned to a specific post
            slug: Limit result set to categories with one or more specific slugs
            
        Returns:
            List of categories
        """
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
        
        return super().list(**params)
    
    def create(
        self,
        name: str,
        slug: str = None,
        parent: int = None,
        description: str = None,
        **kwargs
    ) -> Dict:
        """
        Create a new category
        
        Args:
            name: Name of the category
            slug: Slug for the category (optional)
            parent: Parent category ID (optional)
            description: Description of the category (optional)
            
        Returns:
            Created category data
        """
        data = {"name": name}
        
        if slug is not None:
            data["slug"] = slug
        if parent is not None:
            data["parent"] = parent
        if description is not None:
            data["description"] = description
            
        # Add any additional data
        data.update(kwargs)
        
        return super().create(data)
    
    def update(
        self,
        id: int,
        name: str = None,
        slug: str = None,
        parent: int = None,
        description: str = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing category
        
        Args:
            id: Category ID
            name: Name of the category (optional)
            slug: Slug for the category (optional)
            parent: Parent category ID (optional)
            description: Description of the category (optional)
            
        Returns:
            Updated category data
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        if slug is not None:
            data["slug"] = slug
        if parent is not None:
            data["parent"] = parent
        if description is not None:
            data["description"] = description
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)