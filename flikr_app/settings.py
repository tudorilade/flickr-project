"""
settings.py
---------

Settings module containing constants and credentials for accessing Flickr API
"""
import os

from decouple import config


FLICKR_API_KEY = config("API_KEY")
FLICKR_SECRET_KEY = config("SECRET_KEY")

PATH_TO_MAP = os.path.join(os.getcwd(), "map/map.html")
URL_TO_MAP = f'file://{PATH_TO_MAP}'
FLICKR_PER_PAGE = 500
STOPPING_TIME = 100  # in seconds
