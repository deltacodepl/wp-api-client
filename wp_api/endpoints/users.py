"""
Users endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Users(BaseEndpoint):
    """WordPress Users API wrapper"""
    
    endpoint = "users"
    
    def list(
        self,
        context: str = "view",
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        exclude: Union[int, List[int]] = None,
        include: Union[int, List[int]] = None,
        offset: int = None,
        order: str = "asc",
        orderby: str = "name",
        slug: Union[str, List[str]] = None,
        roles: Union[str, List[str]] = None,
        **kwargs
    ) -> List[Dict]:
        """
        List users with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            offset: Offset the result set by a specific number of items
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (id, name, registered_date, etc.)
            slug: Limit result set to users with one or more specific slugs
            roles: Limit result set to users matching at least one specific role
            
        Returns:
            List of users
        """
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
        if exclude:
            params["exclude"] = exclude if isinstance(exclude, int) else ",".join(map(str, exclude))
        if include:
            params["include"] = include if isinstance(include, int) else ",".join(map(str, include))
        if offset:
            params["offset"] = offset
        if slug:
            params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
        if roles:
            params["roles"] = roles if isinstance(roles, str) else ",".join(roles)
            
        # Add any additional parameters
        params.update(kwargs)
        
        return super().list(**params)
    
    def create(
        self,
        username: str,
        email: str,
        password: str,
        name: str = None,
        first_name: str = None,
        last_name: str = None,
        description: str = None,
        url: str = None,
        roles: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        Create a new user (requires proper authentication with user creation capabilities)
        
        Args:
            username: Username for the user
            email: Email address for the user
            password: Password for the user
            name: Display name for the user
            first_name: First name for the user
            last_name: Last name for the user
            description: Description/bio for the user
            url: URL/website for the user
            roles: List of roles for the user
            
        Returns:
            Created user data
        """
        data = {
            "username": username,
            "email": email,
            "password": password,
        }
        
        if name is not None:
            data["name"] = name
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if description is not None:
            data["description"] = description
        if url is not None:
            data["url"] = url
        if roles is not None:
            data["roles"] = roles
            
        # Add any additional data
        data.update(kwargs)
        
        return super().create(data)
    
    def update(
        self,
        id: int,
        username: str = None,
        email: str = None,
        password: str = None,
        name: str = None,
        first_name: str = None,
        last_name: str = None,
        description: str = None,
        url: str = None,
        roles: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing user
        
        Args:
            id: User ID
            username: Username for the user
            email: Email address for the user
            password: Password for the user
            name: Display name for the user
            first_name: First name for the user
            last_name: Last name for the user
            description: Description/bio for the user
            url: URL/website for the user
            roles: List of roles for the user
            
        Returns:
            Updated user data
        """
        data = {}
        
        if username is not None:
            data["username"] = username
        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        if name is not None:
            data["name"] = name
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if description is not None:
            data["description"] = description
        if url is not None:
            data["url"] = url
        if roles is not None:
            data["roles"] = roles
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)
    
    def me(self, **params) -> Dict:
        """
        Get the current user
        
        Args:
            **params: Query parameters
            
        Returns:
            Current user data
        """
        endpoint = f"{self.endpoint}/me"
        return self.client.get(endpoint, params)