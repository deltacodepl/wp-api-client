"""
Media endpoint for the WordPress REST API
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from .base import BaseEndpoint
import os
import mimetypes


class Media(BaseEndpoint):
    """WordPress Media API wrapper"""
    
    endpoint = "media"
    
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
        parent: Union[int, List[int]] = None,
        parent_exclude: Union[int, List[int]] = None,
        slug: Union[str, List[str]] = None,
        status: Union[str, List[str]] = "inherit",
        media_type: str = None,
        mime_type: str = None,
        **kwargs
    ) -> List[Dict]:
        """
        List media items with various filtering options
        
        Args:
            context: Scope under which the request is made (view, edit, embed)
            page: Current page of the collection
            per_page: Maximum number of items to be returned in result set
            search: Limit results to those matching a string
            after: Limit response to media items published after a given ISO8601 compliant date
            author: Limit result set to media items assigned to specific authors
            author_exclude: Ensure result set excludes media items assigned to specific authors
            before: Limit response to media items published before a given ISO8601 compliant date
            exclude: Ensure result set excludes specific IDs
            include: Limit result set to specific IDs
            offset: Offset the result set by a specific number of items
            order: Order sort attribute ascending or descending (asc, desc)
            orderby: Sort collection by object attribute (date, author, title, etc.)
            parent: Limit result set to items with specific parent IDs
            parent_exclude: Limit result set to all items except those with specific parent IDs
            slug: Limit result set to media items with one or more specific slugs
            status: Limit result set to media items with specific statuses
            media_type: Limit result set to media items with a specific media type
            mime_type: Limit result set to media items with a specific MIME type
            
        Returns:
            List of media items
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
        if parent:
            params["parent"] = parent if isinstance(parent, int) else ",".join(map(str, parent))
        if parent_exclude:
            params["parent_exclude"] = parent_exclude if isinstance(parent_exclude, int) else ",".join(map(str, parent_exclude))
        if slug:
            params["slug"] = slug if isinstance(slug, str) else ",".join(slug)
        if status:
            params["status"] = status if isinstance(status, str) else ",".join(status)
        if media_type:
            params["media_type"] = media_type
        if mime_type:
            params["mime_type"] = mime_type
            
        # Add any additional parameters
        params.update(kwargs)
        
        return super().list(**params)
    
    def upload(
        self,
        file_data: BinaryIO,
        file_name: str = None,
        title: str = None,
        caption: str = None,
        description: str = None,
        alt_text: str = None,
        **kwargs
    ) -> Dict:
        """
        Upload a new media file
        
        Args:
            file_data: File data (file-like object in binary mode)
            file_name: Name of the file
            title: Title for the media item
            caption: Caption for the media item
            description: Description for the media item
            alt_text: Alternative text for the media item
            
        Returns:
            Created media item data
        """
        if file_name is None:
            try:
                file_name = os.path.basename(file_data.name)
            except (AttributeError, TypeError):
                raise ValueError("file_name must be provided when file_data doesn't have a name attribute")
                
        # Get or guess the MIME type
        content_type = mimetypes.guess_type(file_name)[0]
        if content_type is None:
            content_type = 'application/octet-stream'
            
        # Save the original request method
        original_request = self.client.session.request
        
        try:
            # Read file data
            file_content = file_data.read()
            
            # Create a custom request method that properly handles file uploads
            def upload_request_method(method, url, **kwargs):
                headers = kwargs.get('headers', {})
                headers['Content-Type'] = content_type
                headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
                kwargs['headers'] = headers
                
                # Replace json data with binary content for this request
                if 'data' in kwargs:
                    del kwargs['data']
                kwargs['data'] = file_content
                
                return original_request(method, url, **kwargs)
            
            # Temporarily replace the request method
            self.client.session.request = upload_request_method
            
            # Make the request to upload the file
            result = self.client.post(self.endpoint, {})
            
            # Update the media item with additional metadata if provided
            if title or caption or description or alt_text or kwargs:
                media_id = result.get('id')
                if media_id:
                    update_data = {}
                    
                    if title is not None:
                        update_data["title"] = title
                    if caption is not None:
                        update_data["caption"] = caption
                    if description is not None:
                        update_data["description"] = description
                    if alt_text is not None:
                        update_data["alt_text"] = alt_text
                        
                    # Add any additional data
                    update_data.update(kwargs)
                    
                    # Only update if there's data to update
                    if update_data:
                        result = self.update(media_id, **update_data)
                        
            return result
        finally:
            # Restore the original request method
            self.client.session.request = original_request
    
    def update(
        self,
        id: int,
        title: str = None,
        caption: str = None,
        description: str = None,
        alt_text: str = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing media item
        
        Args:
            id: Media item ID
            title: Title for the media item
            caption: Caption for the media item
            description: Description for the media item
            alt_text: Alternative text for the media item
            
        Returns:
            Updated media item data
        """
        data = {}
        
        if title is not None:
            data["title"] = title
        if caption is not None:
            data["caption"] = caption
        if description is not None:
            data["description"] = description
        if alt_text is not None:
            data["alt_text"] = alt_text
            
        # Add any additional data
        data.update(kwargs)
        
        return super().update(id, data)