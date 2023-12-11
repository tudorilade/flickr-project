"""
flikr.py
---------

Main module for the Flickr project. This module contains the logic for accessing and
interacting with the Flickr API. It provides search functionalities on Flickr API for searching
a pattern in tags, title and description of photos. Then, plot the location of the posts upload
on a map.

Classes:
    FlickParser: Main class for interacting with the Flickr API.
"""
import time
from typing import (
    Any,
    Dict,
    List,
    Optional
)

import flickrapi
import folium
from selenium import webdriver

from flikr_app.utils import (
    initialize_flick_api,
    initialize_folium_map,
    start_driver,
    log_info,
    log_error
)
from flikr_app.settings import PATH_TO_MAP, FLICKR_PER_PAGE, STOPPING_TIME


class FlickParser:
    """
    Class to parse the hashtag and limit and queries the Flickr API.

    Attributes:
        flickr (FlickrAPI): a Flickr API instance
        folium_map (folium.Map): a folium map instance to render the posting locations
        driver (selenium.webdriver.Chrome): a driver used to load the posts in real time
        hashtag (str): the hashtag to query the API by
        limit (int): the number of posts to read. By default, the entire posts returned
        current_limit (int): variable to count the number of posts read, only if read-limit is set
    """

    def __init__(self, hashtag: str, limit: Optional[str]):
        """
        Initializes the flickr instance with the given hashtag and limit.

        Args:
            hashtag (str): the hashtag to match against
            limit (int | None): the limit of posts to read. By default, read the entire response.
        """
        self.folium_map: folium.Map = initialize_folium_map()
        self.driver: webdriver.Chrome = start_driver()
        try:
            self.flickr: flickrapi.FlickrAPI = initialize_flick_api()
        except flickrapi.FlickrError as e:
            # stop execution here
            log_error(
                "An error has occurred while connecting to the flickr API. Error: ",
                str(e)
            )
            raise e
        self.hashtag: str = hashtag
        self.limit: Optional[int] = limit
        self.current_limit = 0
        log_info(f"Hashtag inserted: {self.hashtag} with limit: {self.limit}")

    def __enter__(self):
        """
        Magic method to enter the context
        """
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        The main reason I implemented a context manager was to ensure that I close the
        driver after executing the code, regardless of how it exists.
        """
        self.driver.quit()
        # Handle exceptions if necessary
        if exception_type is not None:
            # log the traceback
            log_error("", str(exception_value))

        # suppress here the exception in case it exists
        return True

    def parse(self) -> None:
        """Parse images

        Method responsible for sending the request to flickr API and process the most recent
        uploaded images matching the hashtag.

        Their API will match pictures against hashtag using tags, description and title fields.
        It is sufficient for the hashtag to be present in only one.
        """
        query_params = {
            "page": 1,
            "extras": "geo,tags,description",
            "per_page": FLICKR_PER_PAGE,
            "has_geo": True,
            # returns pictures that match the hashtag in desc order of upload
            "sort": "date-posted-desc",
            "text": self.hashtag
        }

        # retrieving the first page of the most recent uploaded images
        try:
            photos = self.flickr.photos.search(**query_params).get("photos")
        except flickrapi.FlickrError as e:
            # stop execution here
            log_error(
                "An error has occurred while accessing the flickr API. Error: ",
                str(e)
            )
            raise e

        # assumptions that their API works as expected
        assert "photo" in photos
        assert isinstance(photos["photo"], list), \
            "Photos must be a list. Weird response from flickr"
        assert isinstance(photos["pages"], int), "The number of pages should be an integer"

        if len(photos["photo"]) == 0:
            # check if any photos are returned
            log_info(f"No images were returned for this hashtag: {self.hashtag}")
            return

        total_pages = photos["pages"]  # guarantee is an integer

        # if only one page returned, then process only that. otherwise, start with page 2.
        # the indexing on flickr API starts from 1
        start = 0 if total_pages == 1 else 2

        log_info(f"Starting to process the images")
        for page in range(start, total_pages):
            log_info(f"Processing the page: {page}")
            processed = self.process_photo_page(page, photos["photo"])
            if not processed:
                # stop execution after finalized to process the photos after limit reached
                # or no more photos to process
                break

            query_params["page"] = page

            try:
                photos = self.flickr.photos.search(**query_params).get("photos")
            except flickrapi.FlickrError as e:
                # stop execution here
                log_error(
                    "An error has occurred while accessing the flickr API. Error: ",
                    str(e)
                )
                raise e

        self.folium_map.save(PATH_TO_MAP)
        self.driver.refresh()
        log_info(f"Sleeping for: {STOPPING_TIME}s just to show the final result")
        time.sleep(STOPPING_TIME)

    def process_photo_page(self, page: int, photos: List[Dict[str, Any]]) -> bool:
        """Process photo

        Method responsible for processing all photos returned by Flickr API on current page.

        Args:
            page (int): Current page
            photos (List[Dict[str, Any]]): a list of photos to process

        Returns:
            True or False: True if process entire pages, False if an error occurred or limit reached
        """
        if not photos:
            log_info(f"No photos on page: {page}")
            return False

        for photo in photos:
            if self.limit and self.current_limit >= self.limit:
                log_info(f"Limit of {self.limit} reached. Stop processing the photos")
                return False

            lat, long = photo["latitude"], photo["longitude"]

            folium.Marker(
                location=[lat, long],
                popup=photo["title"],
                icon=folium.Icon(icon="cloud", color="blue"),
            ).add_to(self.folium_map)

            if self.limit:
                self.current_limit += 1
                log_info(f"Number of photo processed: {self.current_limit}")

        self.folium_map.save(PATH_TO_MAP)
        self.driver.refresh()
        return True
