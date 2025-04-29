========
Examples
========

This section provides practical examples of using the WordPress REST API Python Client.

Basic Usage
----------

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import ApplicationPasswordAuth

    # Initialize client with Application Password authentication
    auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)

    # Get all published posts
    posts = client.posts.list(status="publish")
    for post in posts:
        print(f"Post ID: {post['id']}, Title: {post['title']['rendered']}")

    # Create a new post
    new_post = client.posts.create(
        title="Hello World",
        content="This is my first post created with the WordPress REST API Python client!",
        status="publish"
    )

Working with Posts
-----------------

Listing Posts with Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get recent posts
    recent_posts = client.posts.list(
        per_page=5,
        status="publish",
        orderby="date",
        order="desc"
    )

    # Get posts by category
    posts_in_category = client.posts.list(
        categories=5,
        per_page=10
    )

    # Get posts by author
    author_posts = client.posts.list(
        author=12,
        status="publish"
    )

    # Search posts
    search_results = client.posts.list(
        search="wordpress",
        per_page=20
    )

Creating and Updating Posts
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create a draft post
    draft_post = client.posts.create(
        title="My Draft Post",
        content="This is a draft post content.",
        status="draft"
    )

    # Create a published post with categories and tags
    published_post = client.posts.create(
        title="My Published Post",
        content="This is the content of my published post.",
        excerpt="A short excerpt for the post.",
        status="publish",
        categories=[5, 7],
        tags=[12, 15],
        featured_media=42
    )

    # Update a post
    updated_post = client.posts.update(
        123,
        title="Updated Title",
        content="This content has been updated."
    )

    # Change a post's status from draft to publish
    published = client.posts.update(
        123,
        status="publish"
    )

Working with Custom Post Types
----------------------------

.. code-block:: python

    # Get a custom post type handler
    products = client.get_custom_post_type("product")

    # List products
    all_products = products.list(per_page=20)

    # Get a specific product
    product = products.get(123)

    # Create a product
    new_product = products.create(
        title="New Product",
        status="publish",
        content="Product description",
        # Any custom fields
        meta={"regular_price": "19.99", "sale_price": "14.99"}
    )

    # Get product meta
    product_meta = products.get_meta()
    price = product_meta.get(123, "regular_price")

Error Handling
------------

.. code-block:: python

    from wp_api import WPClient
    from wp_api.auth import ApplicationPasswordAuth
    from wp_api.exceptions import (
        WPAPIError,
        WPAPIAuthError,
        WPAPIRequestError,
        WPAPINotFoundError,
        WPAPIPermissionError,
        WPAPIValidationError
    )

    try:
        auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
        client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
        
        # Try to access a non-existent post
        post = client.posts.get(999999)
        
    except WPAPIAuthError as e:
        print(f"Authentication error: {e}")
        
    except WPAPIPermissionError as e:
        print(f"Permission denied: {e}")
        
    except WPAPINotFoundError as e:
        print(f"Resource not found: {e}")
        
    except WPAPIValidationError as e:
        print(f"Validation error: {e}")
        print(f"Error data: {e.error_data}")
        
    except WPAPIError as e:
        print(f"WordPress API error: {e}")

Working with Media
----------------

Uploading Files
~~~~~~~~~~~~~

.. code-block:: python

    # Upload an image file
    with open("image.jpg", "rb") as img_file:
        uploaded_image = client.media.upload(
            img_file,
            title="My Uploaded Image",
            alt_text="An image description for accessibility",
            caption="This is the image caption"
        )
        
        # Use the uploaded media in a post
        client.posts.create(
            title="Post with Image",
            content="Post content",
            featured_media=uploaded_image["id"],
            status="publish"
        )

More Examples
-----------

For more examples, check the examples directory in the GitHub repository:

* Working with custom taxonomies
* Managing users
* Handling comments
* Working with WordPress settings
* Advanced error handling scenarios