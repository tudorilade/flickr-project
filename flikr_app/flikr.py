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
import os
import subprocess
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
    log_error,
    validate_api_response
)
from flikr_app.settings import PATH_TO_MAP, FLICKR_PER_PAGE


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
        refresh_map_after (int): whether to refresh the map or not after processing a
        number of photos. default is driver refreshes after each processed page.
    """

    def __init__(self, hashtag: str, limit: Optional[str], refresh_map_after: int):
        """
        Initializes the flickr instance with the given hashtag and limit.

        Args:
            hashtag (str): the hashtag to match against
            limit (int | None): the limit of posts to read. By default, read the entire response.
            refresh_map_after (int): whether to refresh the map after custom threshold

        Raise:
            flickrapi.FlickrError: if the connection with flickrapi fails
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
        self.refresh_map_after = refresh_map_after
        log_info(
            f"Hashtag inserted: {self.hashtag} with limit: {self.limit} "
            f"and refresh {self.refresh_map_after}"
        )

    def __enter__(self):
        """
        Magic method to enter the context. If last map exists, it deletes to allow the creation
        of a fresh new one.
        """
        if os.path.exists(PATH_TO_MAP):
            # clear the old map if exists and refresh it
            os.remove(PATH_TO_MAP)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        The main reason I implemented a context manager was to ensure that I close the
        driver after executing the code, regardless of how it exists. I implemented a sleep
        just to stop the execution and look at the rendered map. The driver has the purpose to show
        in real time the response on map. After it finishes, it will open a new map independent
        of the application.
        """
        self.driver.quit()
        self.folium_map.save(PATH_TO_MAP)
        subprocess.run(["open", PATH_TO_MAP])
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
        photos = self.get_photos(query_params)

        if len(photos["photo"]) == 0:
            # check if any photos are returned
            log_info(f"No images were returned for this hashtag: {self.hashtag}")
            return

        total_pages = photos["pages"]  # guarantee is an integer

        # if only one page returned, then process only that. otherwise, start with page 2.
        # the indexing on flickr API starts from 1
        start = 0 if total_pages == 1 else 2

        log_info(f"Starting to process {photos['total']} images")

        for page in range(start, total_pages):
            log_info(f"Processing the page: { page + 1 if not bool(start) else page - 1}")
            processed = self.process_photo_page(page, photos["photo"])
            if not processed:
                # stop execution after finalized to process the photos after limit reached
                # or no more photos to process
                break

            # get next page
            query_params["page"] = page
            photos = self.get_photos(query_params)

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

            self.add_pin(photo["latitude"], photo["longitude"], photo["title"])
            self.current_limit += 1

            # if refresh_map is inserted and if it passes a threshold, refresh the map
            if bool(self.refresh_map_after) and self.current_limit % self.refresh_map_after == 0:
                self.map_refresh()

        if not bool(self.refresh_map_after):
            # if refresh map is not inserted, refresh after a page is processed
            self.map_refresh()

        log_info(f"Number of photo processed: {self.current_limit}")
        return True


    def get_photos(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get photos

        Retrieve all photos matching query_params

        Args:
            query_params (dict): a kwargs query param to pass to API call

        Returns:
            A dictionary representing the returned photos

        Raise:
            FlikrException: if the request couldn't be processed by Flickr API
        """
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
        else:
            # assumptions that their API works as expected
            validate_api_response(photos)
            return photos

    def map_refresh(self) -> None:
        """
        Helper method for refreshing the driver and map
        """
        self.folium_map.save(PATH_TO_MAP)
        self.driver.refresh()

    def add_pin(self, lat: float, long: float, title: str) -> None:
        """
        Helper method responsible for adding a pin to the folium map.

        Args:
            lat (float): The latitude of the photo
            long (float): The longitude of the photo
            title (str): The title of the photo
        """
        folium.Marker(
            location=[lat, long],
            popup=title,
            icon=folium.Icon(icon="cloud", color="blue"),
        ).add_to(self.folium_map)
