"""
main.py
________

Main module of the application.
This is the entry point of the application. It parses the arguments from CLI based on the
definition of ArgumentParser class.
"""
import argparse

from flikr_app import FlickParser


def main() -> None:
    """
    Main function to parse command line arguments and initiate parsing process.

    This function constructs a CLI argument parser for Flickr project.
    It accepts a mandatory hashtag argument and an optional limit argument from the command line.
    After parsing these arguments, it invokes parse function to process the hashtag and limit.
    """

    cli_parser = argparse.ArgumentParser(
        prog="flickr", description="CLI interface for flickr", add_help=True
    )
    cli_parser.add_argument(
        "--hashtag",
        "-t",
        help="Target hashtag to look for."
             " For better searching, you can skip '#' at the beginning of word",
        required=True,
    )
    cli_parser.add_argument(
        "--limit",
        "-l",
        help="The limit on how much posts to pin on map. Default behavior is to read all posts",
        required=False,
        type=int
    )
    cli_parser.add_argument(
        "--refresh_map_after",
        "-rfa",
        help="Default behavior is for the map to refresh after parsing a page from API. IT is "
             "recommended to specify after how many processed entries the map should be refreshed."
             " It can slow down the rendered map. default is 0, meaning that will refresh "
             "after parsing a page from Flickr API",
        required=False,
        type=int,
        default=0
    )

    args = cli_parser.parse_args()
    hashtag = args.hashtag
    limit = int(args.limit) if args.limit else None
    refresh_map_after = args.refresh_map_after

    with FlickParser(hashtag=hashtag, limit=limit, refresh_map_after=refresh_map_after) as parser:
        parser.parse()


if __name__ == "__main__":
    main()
