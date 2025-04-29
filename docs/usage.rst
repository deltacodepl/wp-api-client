=====
Usage
=====

To use the WordPress REST API Python Client in a project::

    from wp_api import WPClient
    from wp_api.auth import ApplicationPasswordAuth

    # Initialize client with Application Password authentication
    auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)

    # Get all published posts
    posts = client.posts.list(status="publish")
    for post in posts:
        print(f"Post ID: {post['id']}, Title: {post['title']['rendered']}")

Authentication Methods
---------------------

The library supports multiple authentication methods:

Application Passwords (Recommended for WordPress 5.6+)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import ApplicationPasswordAuth

    auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)

Basic Authentication
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import BasicAuth

    auth = BasicAuth(username="your_username", password="your_password")
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)

OAuth1 Authentication
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import OAuth1

    auth = OAuth1(
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret",
        token="your_token",
        token_secret="your_token_secret"
    )
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)

Working with Posts
----------------

.. code-block:: python

    # List posts with filtering
    recent_posts = client.posts.list(
        per_page=5,
        status="publish",
        orderby="date",
        order="desc"
    )

    # Get a specific post
    post = client.posts.get(123)

    # Create a new post
    new_post = client.posts.create(
        title="My New Post",
        content="This is the content of my post.",
        status="publish",
        categories=[5, 7],
        tags=[12, 15]
    )

    # Update a post
    updated_post = client.posts.update(
        123,
        title="Updated Title",
        content="Updated content"
    )

    # Delete a post
    client.posts.delete(123)

Working with Media
----------------

.. code-block:: python

    # List media items
    media_items = client.media.list()

    # Upload a new image
    with open("image.jpg", "rb") as image_file:
        media = client.media.upload(
            image_file,
            file_name="my-image.jpg",
            title="My Image",
            alt_text="Description of my image"
        )

    # Update media metadata
    updated_media = client.media.update(
        456,
        title="Updated Image Title",
        alt_text="Updated alt text"
    )

Error Handling
------------

The library provides specific exception types for different error scenarios:

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import ApplicationPasswordAuth
    from wp_api.exceptions import (
        WPAPIError,
        WPAPIAuthError,
        WPAPIRequestError,
        WPAPIRateLimitError,
        WPAPINotFoundError,
        WPAPIPermissionError
    )

    try:
        auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
        client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
        
        # Try to access a resource
        post = client.posts.get(999999)  # Non-existent post ID
        
    except WPAPIAuthError as e:
        print(f"Authentication error: {e}")
        
    except WPAPIPermissionError as e:
        print(f"Permission denied: {e}")
        
    except WPAPINotFoundError as e:
        print(f"Resource not found: {e}")
        
    except WPAPIRateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        
    except WPAPIRequestError as e:
        print(f"Request error: {e}")
        print(f"Status code: {e.status_code}")
        
    except WPAPIError as e:
        print(f"WordPress API error: {e}")

For more detailed examples, refer to the examples directory in the repository.