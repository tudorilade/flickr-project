import argparse

from flikr_app.flikr import FlickParser


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
        required=True
    )
    cli_parser.add_argument(
        "--limit",
        "-l",
        help="The limit on how much posts to pin on map. Default behavior is to read all posts",
        required=False,
        type=int
    )

    args = cli_parser.parse_args()
    hashtag = args.hashtag
    limit = int(args.limit) if args.limit else None

    with FlickParser(hashtag=hashtag, limit=limit) as parser:
        parser.parse()


if __name__ == "__main__":
    main()
