from typing import Optional

from flikr_app.flikr import FlickParser



def parse(hashtag: str, limit: Optional[int]) -> None:
    """Parser

    Method responsible for invoking process images with the hashtag and limit inserted from CLI.

    Args:
        hashtag (str): the hashtag inserted from CLI
        limit (int): the number of photos to process. If not specified, all photos will be processed

    Returns:
        None
    """
    FlickParser(
        hashtag=hashtag,
        limit=limit
    ).parse()
