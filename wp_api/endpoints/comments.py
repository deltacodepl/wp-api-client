"""
Comments endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseEndpoint


class Comments(BaseEndpoint):
    """WordPress Comments API wrapper"""
    
    endpoint = "comments"
    
    def list(
        self,
        context: str = "view",
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        after: str = None,
        author: Union[int, List[int]] = None,
        author_exclude: Union[int, List[int]] = None,
        author_email: str = None,
        before: str = None,
        exclude: Union[int, List[int]] = None,
        include: Union[int, List[int]] = None,
        offset: int = None,
        order: str = "desc",
        orderby: str = "date_gmt",
        parent: Union[int, List[int]] = None,
        parent_exclude: Union[int, List[int]] = None,
        post: Union[int, List[int]] = None,
        status: str = "approve",
        type: str = "comment",
        password: str = None,
        **kwargs
    ) -> List[Dict]:
        """
        List comments with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            after: Limit response to comments published after a given ISO8601 compliant date
            author: Limit result set to comments assigned to specific authors
            author_exclude: Ensure result set excludes comments assigned to specific authors
            author_email: Limit result set to comments with a specific author email
            before: Limit response to comments published before a given ISO8601 compliant date
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            offset: Offset the result set by a specific number of items
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (date, id, include, post, parent, type)
            parent: Limit result set to comments with specific parent IDs
            parent_exclude: Limit result set to all items except those with specific parent IDs
            post: Limit result set to comments assigned to specific posts
            status: Limit result set to comments with a specific status (approve, hold, spam, trash)
            type: Limit result set to comments with a specific type (comment, pingback, trackback)
            password: Filter comments by post password, if the post is password protected
            
        Returns:
            List of comments
        """
        params = {
            "context": context,
            "page": page,
            "per_page": per_page,
            "order": order,
            "orderby": orderby,
            "status": status,
            "type": type,
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
        if author_email:
            params["author_email"] = author_email
        if before:
            params["before"] = before
        if exclude:
            params["exclude"] = exclude if isinstance(exclude, int) else ",".join(map(str, exclude))
        if include:
            params["include"] = include if isinstance(include, int) else ",".join(map(str, include))
        if offset:
            params["offset"] = offset
        if parent:
            params["parent"] = parent if isinstance(parent, int) else ",".join(map(str, parent))
        if parent_exclude:
            params["parent_exclude"] = parent_exclude if isinstance(parent_exclude, int) else ",".join(map(str, parent_exclude))
        if post:
            params["post"] = post if isinstance(post, int) else ",".join(map(str, post))
        if password:
            params["password"] = password
            
        # Add any additional parameters
        params.update(kwargs)
        
        return super().list(**params)
    
    def create(
        self,
        post: int,
        content: str,
        author: int = None,
        author_name: str = None,
        author_email: str = None,
        author_url: str = None,
        parent: int = None,
        status: str = None,
        **kwargs
    ) -> Dict:
        """
        Create a new comment
        
        Args:
            post: Post ID to which the comment belongs
            content: Content of the comment
            author: User ID of the comment author (if registered)
            author_name: Name of the comment author (if not registered)
            author_email: Email of the comment author (if not registered)
            author_url: URL/website of the comment author (if not registered)
            parent: Parent comment ID (for threaded comments)
            status: Comment status (approve, hold, spam, trash)
            
        Returns:
            Created comment data
        """
        data = {
            "post": post,
            "content": content,
        }
        
        if author is not None:
            data["author"] = author
        if author_name is not None:
            data["author_name"] = author_name
        if author_email is not None:
            data["author_email"] = author_email
        if author_url is not None:
            data["author_url"] = author_url
        if parent is not None:
            data["parent"] = parent
        if status is not None:
            data["status"] = status
            
        # Add any additional data
        data.update(kwargs)
        
        return super().create(data)
    
    def update(
        self,
        id: int,
        content: str = None,
        author: int = None,
        author_name: str = None,
        author_email: str = None,
        author_url: str = None,
        post: int = None,
        parent: int = None,
        status: str = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing comment
        
        Args:
            id: Comment ID
            content: Content of the comment
            author: User ID of the comment author (if registered)
            author_name: Name of the comment author (if not registered)
            author_email: Email of the comment author (if not registered)
            author_url: URL/website of the comment author (if not registered)
            post: Post ID to which the comment belongs
            parent: Parent comment ID (for threaded comments)
            status: Comment status (approve, hold, spam, trash)
            
        Returns:
            Updated comment data
        """
        data = {}
        
        if content is not None:
            data["content"] = content
        if author is not None:
            data["author"] = author
        if author_name is not None:
            data["author_name"] = author_name
        if author_email is not None:
            data["author_email"] = author_email
        if author_url is not None:
            data["author_url"] = author_url
        if post is not None:
            data["post"] = post
        if parent is not None:
            data["parent"] = parent
        if status is not None:
            data["status"] = status
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)