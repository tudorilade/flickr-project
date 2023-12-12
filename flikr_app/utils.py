"""
utils.py
---------

Utility module containing helping functions related to Flickr API interaction.

Functions:
    start_driver: starts the chrome driver where the map is rendered
    initialize_flick_api: initialize a Flickr API client
    initialize_folium_map: initialize the folium map used for pinning the locations
    log_error(message, error): writes the error message to standard error
    log_info(message): writes the info message to standard output
"""
import sys
from typing import Any, Dict

import flickrapi
import folium
from selenium import webdriver

from flikr_app.settings import (
    FLICKR_API_KEY,
    FLICKR_SECRET_KEY,
    PATH_TO_MAP,
    URL_TO_MAP
)


def start_driver() -> webdriver.Chrome:
    """
    Method responsible for starting the driver where the map will be rendered
    :return webdriver.Chrome: Chrome driver
    """
    driver = webdriver.Chrome()
    driver.get(URL_TO_MAP)
    return driver


def initialize_flick_api() -> flickrapi.FlickrAPI:
    """
    Method responsible for initializing the Flickr API which will be used to retrieve
    the most recent posts from flickr.

    Returns:
        flickrapi.FlickrAPI: Flickr API instance which returns responses in json format
    """
    return flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_SECRET_KEY, format='parsed-json')


def initialize_folium_map() -> folium.Map:
    """
    Method responsible for initializing the folium MAP with a start zoom of 1. It saves an HTML
    in map/ directory.

    Returns:
        folium.Map: a folium Map instance which pin the locations from where photo were uploaded
    """
    render_map = folium.Map(location=(30, 10), zoom_start=3)
    render_map.save(PATH_TO_MAP)
    return render_map


def validate_api_response(photos: Dict[str, Any]) -> None:
    """Assumptions for Flickr API response

    The API response must have a photo list as response where each individual photo
    is displayed and the page must be an integer and passed.

    Raise:
        Assertion error in case of unexpected response from Flickr API
    """
    # assumptions that their API works as expected
    assert "photo" in photos, "Photo key is missing"
    assert isinstance(photos["photo"], list), \
        "Photos must be a list. Weird response from flickr"
    assert isinstance(photos["pages"], int), "The number of pages should be an integer"


def log_error(message: str, error: str) -> None:
    """Log error

    Method responsible for logging an error to stderr.

    Args:
        message (str): the message to be logged
        error (str): the errror to be logged

    Returns:
        None
    """
    sys.stderr.write(message)
    sys.stderr.write(error)
    sys.stderr.write("\n")
    sys.stderr.flush()


def log_info(message: str) -> None:
    """Log Info

    Method responsible for logging a message to stdout.

    Args:
        message (str): the message to be logged

    Returns:
        None
    """
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()
