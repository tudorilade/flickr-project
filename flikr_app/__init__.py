"""
flick_app
---------

The `flick_app` package is designed for interacting with the Flickr API.
 It provides search functionalities on Flickr API based on an input string.

This package contains the `FlickParser` class, responsible for parsing the Flickr API
response to a folium Map.

Modules:
    flikr: Contains the `FlickParser` class responsible for parsing the Flickr API.
    settings: Contains settings for the `FlickParser`, such as credentials, constants etc.
    utils: Contains utility functions for the `FlickParser`

Usage:
    To use the `FlickParser` class, import it from the package and create an instance:

    from flick_app import FlickParser

    with FlickParser(hashtag, limit) as parser:
        parser.parse()
Note:
    Ensure you have the necessary Flickr API credentials before using the
     `FlickParser` class for API interactions. Create an .env file with the following
     information:

        API_KEY=api_key

        SECRET_KEY=secret_key
"""
from .flikr import FlickParser

__all__ = ['FlickParser']
