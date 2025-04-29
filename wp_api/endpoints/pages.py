"""
Pages endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Pages(BaseEndpoint):
    """WordPress Pages API wrapper"""
    
    endpoint = "pages"
    
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
        menu_order: int = None,
        offset: int = None,
        order: str = "desc",
        orderby: str = "date",
        parent: Union[int, List[int]] = None,
        parent_exclude: Union[int, List[int]] = None,
        slug: Union[str, List[str]] = None,
        status: Union[str, List[str]] = "publish",
        **kwargs
    ) -> List[Dict]:
        """
        List pages with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            after: Limit response to pages published after a given ISO8601 compliant date
            author: Limit result set to pages assigned to specific authors
            author_exclude: Ensure result set excludes pages assigned to specific authors
            before: Limit response to pages published before a given ISO8601 compliant date
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            menu_order: Limit result set to pages with a specific menu_order value
            offset: Offset the result set by a specific number of items
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (date, author, title, etc.)
            parent: Limit result set to items with particular parent IDs
            parent_exclude: Limit result set to all items except those with specific parent IDs
            slug: Limit result set to pages with one or more specific slugs
            status: Limit result set to pages with specific statuses
            
        Returns:
            List of pages
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
        if menu_order:
            params["menu_order"] = menu_order
        if offset:
            params["offset"] = offset
        if parent:
            params["parent"] = parent if isinstance(parent, int) else ",".join(map(str, parent))
        if parent_exclude:
            params["parent_exclude"] = parent_exclude if isinstance(parent_exclude, int) else ",".join(map(str, parent_exclude))
        if slug:
            params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
        if status:
            params["status"] = status if isinstance(status, str) else ",".join(status)
            
        # Add any additional parameters
        params.update(kwargs)
        
        return super().list(**params)
    
    def create(
        self,
        title: str,
        content: str = None,
        excerpt: str = None,
        status: str = "publish",
        author: int = None,
        featured_media: int = None,
        comment_status: str = None,
        ping_status: str = None,
        menu_order: int = None,
        parent: int = None,
        template: str = None,
        **kwargs
    ) -> Dict:
        """
        Create a new page
        
        Args:
            title: Page title
            content: Page content
            excerpt: Page excerpt
            status: Page status (publish, future, draft, pending, private)
            author: Page author ID
            featured_media: Featured image ID
            comment_status: Whether comments are allowed (open, closed)
            ping_status: Whether pings are allowed (open, closed)
            menu_order: The order in which the page should appear in menus
            parent: Parent page ID
            template: Page template to use
            
        Returns:
            Created page data
        """
        data = {"title": title}
        
        if content is not None:
            data["content"] = content
        if excerpt is not None:
            data["excerpt"] = excerpt
        if status is not None:
            data["status"] = status
        if author is not None:
            data["author"] = author
        if featured_media is not None:
            data["featured_media"] = featured_media
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if menu_order is not None:
            data["menu_order"] = menu_order
        if parent is not None:
            data["parent"] = parent
        if template is not None:
            data["template"] = template
            
        # Add any additional data
        data.update(kwargs)
        
        return super().create(data)
    
    def update(
        self,
        id: int,
        title: str = None,
        content: str = None,
        excerpt: str = None,
        status: str = None,
        author: int = None,
        featured_media: int = None,
        comment_status: str = None,
        ping_status: str = None,
        menu_order: int = None,
        parent: int = None,
        template: str = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing page
        
        Args:
            id: Page ID
            title: Page title
            content: Page content
            excerpt: Page excerpt
            status: Page status (publish, future, draft, pending, private)
            author: Page author ID
            featured_media: Featured image ID
            comment_status: Whether comments are allowed (open, closed)
            ping_status: Whether pings are allowed (open, closed)
            menu_order: The order in which the page should appear in menus
            parent: Parent page ID
            template: Page template to use
            
        Returns:
            Updated page data
        """
        data = {}
        
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if excerpt is not None:
            data["excerpt"] = excerpt
        if status is not None:
            data["status"] = status
        if author is not None:
            data["author"] = author
        if featured_media is not None:
            data["featured_media"] = featured_media
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if menu_order is not None:
            data["menu_order"] = menu_order
        if parent is not None:
            data["parent"] = parent
        if template is not None:
            data["template"] = template
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)
    
    def get_revisions(self, page_id: int, **params) -> List[Dict]:
        """
        Get page revisions
        
        Args:
            page_id: Page ID
            **params: Query parameters
            
        Returns:
            List of page revisions
        """
        endpoint = f"{self.endpoint}/{page_id}/revisions"
        return self.client.get(endpoint, params)
    
    def get_revision(self, page_id: int, revision_id: int, **params) -> Dict:
        """
        Get a specific page revision
        
        Args:
            page_id: Page ID
            revision_id: Revision ID
            **params: Query parameters
            
        Returns:
            Page revision data
        """
        endpoint = f"{self.endpoint}/{page_id}/revisions/{revision_id}"
        return self.client.get(endpoint, params)