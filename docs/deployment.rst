==========
Deployment
==========

This guide explains how to deploy the WordPress REST API Python Client to PyPI and update the documentation on Read the Docs.

Preparing for Release
-------------------

Before releasing a new version, make sure to:

1. Update the version number in ``wp_api/__init__.py``
2. Update the ``HISTORY.rst`` file with the new version and changes
3. Make sure all tests pass
4. Generate and review the documentation

Building the Package
------------------

You can use the provided Makefile to build the distribution packages:

.. code-block:: bash

    make dist

This will generate both a source distribution and a wheel in the ``dist/`` directory.

Publishing to PyPI
----------------

To publish the package to PyPI:

1. First, make sure you have all the necessary credentials set up:

   .. code-block:: bash

       pip install twine
       
   Create or update your ``.pypirc`` file:

   .. code-block:: ini
       
       [distutils]
       index-servers =
           pypi
           testpypi
       
       [pypi]
       username = __token__
       password = pypi-your-api-token
       
       [testpypi]
       repository = https://test.pypi.org/legacy/
       username = __token__
       password = pypi-test-your-api-token

2. Test your package on TestPyPI first:

   .. code-block:: bash

       twine upload --repository testpypi dist/*

3. Once you've verified everything works on TestPyPI, upload to the real PyPI:

   .. code-block:: bash

       twine upload dist/*

   Or use the Makefile:

   .. code-block:: bash

       make release

Updating Documentation on Read the Docs
-------------------------------------

The documentation on Read the Docs is automatically built when you push changes to your GitHub repository.

To set up Read the Docs integration:

1. Go to https://readthedocs.org/ and sign in with your GitHub account
2. Import your repository
3. Configure the documentation settings:
   - Make sure the correct documentation directory is set (``docs/``)
   - Select appropriate Python version
   - Enable "Install project" option to ensure dependencies are installed

For manual documentation builds:

.. code-block:: bash

    make docs

This will generate HTML documentation in ``docs/_build/html/`` that you can review locally.

Tagging Releases on GitHub
------------------------

After publishing to PyPI, it's good practice to tag the release on GitHub:

.. code-block:: bash

    git tag -a v0.1.0 -m "Release version 0.1.0"
    git push origin v0.1.0

This helps users find specific versions of the code that match the PyPI releases.

Automating with GitHub Actions
---------------------------

You can automate the release process using GitHub Actions. Here's a sample workflow file (``.github/workflows/release.yml``):

.. code-block:: yaml

    name: Release

    on:
      release:
        types: [created]

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.9'
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install build twine
        - name: Build and publish
          env:
            TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
            TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
          run: |
            python -m build
            twine upload dist/*