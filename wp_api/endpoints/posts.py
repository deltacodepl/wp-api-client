"""
Posts endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Posts(BaseEndpoint):
    """WordPress Posts API wrapper"""
    
    endpoint = "posts"
    
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
        categories: Union[int, List[int]] = None,
        categories_exclude: Union[int, List[int]] = None,
        tags: Union[int, List[int]] = None,
        tags_exclude: Union[int, List[int]] = None,
        sticky: bool = None,
        tax_relation: str = None,
        **kwargs
    ) -> List[Dict]:
        """
        List posts with various filtering options
        
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
            categories: Limit result set to items with specific categories
            categories_exclude: Limit result set to items without specified categories
            tags: Limit result set to items with specific tags
            tags_exclude: Limit result set to items without specific tags
            sticky: Limit result set to items that are sticky
            tax_relation: Taxonomy relationship (AND/OR)
            
        Returns:
            List of posts
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
        if offset:
            params["offset"] = offset
        if slug:
            params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
        if status:
            params["status"] = status if isinstance(status, str) else ",".join(status)
        if categories:
            params["categories"] = categories if isinstance(categories, int) else ",".join(map(str, categories))
        if categories_exclude:
            params["categories_exclude"] = categories_exclude if isinstance(categories_exclude, int) else ",".join(map(str, categories_exclude))
        if tags:
            params["tags"] = tags if isinstance(tags, int) else ",".join(map(str, tags))
        if tags_exclude:
            params["tags_exclude"] = tags_exclude if isinstance(tags_exclude, int) else ",".join(map(str, tags_exclude))
        if sticky is not None:
            params["sticky"] = "true" if sticky else "false"
        if tax_relation:
            params["tax_relation"] = tax_relation
            
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
        format: str = None,
        categories: List[int] = None,
        tags: List[int] = None,
        **kwargs
    ) -> Dict:
        """
        Create a new post
        
        Args:
            title: Post title
            content: Post content
            excerpt: Post excerpt
            status: Post status (publish, future, draft, pending, private)
            author: Post author ID
            featured_media: Featured image ID
            comment_status: Whether comments are allowed (open, closed)
            ping_status: Whether pings are allowed (open, closed)
            format: Post format (standard, aside, chat, gallery, link, image, quote, status, video, audio)
            categories: List of category IDs
            tags: List of tag IDs
            
        Returns:
            Created post data
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
        if format is not None:
            data["format"] = format
        if categories is not None:
            data["categories"] = categories
        if tags is not None:
            data["tags"] = tags
            
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
        format: str = None,
        categories: List[int] = None,
        tags: List[int] = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing post
        
        Args:
            id: Post ID
            title: Post title
            content: Post content
            excerpt: Post excerpt
            status: Post status (publish, future, draft, pending, private)
            author: Post author ID
            featured_media: Featured image ID
            comment_status: Whether comments are allowed (open, closed)
            ping_status: Whether pings are allowed (open, closed)
            format: Post format (standard, aside, chat, gallery, link, image, quote, status, video, audio)
            categories: List of category IDs
            tags: List of tag IDs
            
        Returns:
            Updated post data
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
        if format is not None:
            data["format"] = format
        if categories is not None:
            data["categories"] = categories
        if tags is not None:
            data["tags"] = tags
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)
    
    def get_revisions(self, post_id: int, **params) -> List[Dict]:
        """
        Get post revisions
        
        Args:
            post_id: Post ID
            **params: Query parameters
            
        Returns:
            List of post revisions
        """
        endpoint = f"{self.endpoint}/{post_id}/revisions"
        return self.client.get(endpoint, params)
    
    def get_revision(self, post_id: int, revision_id: int, **params) -> Dict:
        """
        Get a specific post revision
        
        Args:
            post_id: Post ID
            revision_id: Revision ID
            **params: Query parameters
            
        Returns:
            Post revision data
        """
        endpoint = f"{self.endpoint}/{post_id}/revisions/{revision_id}"
        return self.client.get(endpoint, params)