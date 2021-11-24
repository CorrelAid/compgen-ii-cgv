import argparse
import json
import pprint
import textwrap

import pandas as pd

from compgen2.correction import Preprocessing
from compgen2.gov import Gov, Matcher


def parse_args():
    parser = argparse.ArgumentParser(
        prog="compgen2 GOV matcher",
        description=textwrap.dedent(
            """***compgen2 GOV matcher***

A simple cli tool to match a single location name or a list of location names against the GOV db.

*Note*: The necessary data for this program can be found in the Nextcloud under https://correlcloud.org.
"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-l", "--location", help="Location you want to match against the GOV db.")
    parser.add_argument("-f", "--file", help="TXT file with location names, one name per line.")
    parser.add_argument("-d", "--data-root", required=True, help="Path to the local data root directory.")
    parser.add_argument("-p", "--use-preprocessing", action="store_true")

    return parser.parse_args()


def get_match(location: str, preprocessing: bool, data_root: str) -> dict:
    """Find possible matches for a single query location.

    Args:
        location (str): location name you want to match.
        preprocessing (bool): preprocess location before matching.
        data_root (str): root directory holding the data.

    Returns:
        str: json representation of the result string.
    """
    gov = Gov(data_root)
    gov.load_data()
    gov.build_indices()

    m = Matcher(gov)
    m.get_match_for_locations([location])

    return m.results[location]


def get_matches(locations: list[str], preprocessing: bool, data_root: str) -> dict:
    """Find possible matches for all locations.

    Args:
        locations (list[str]): list of location names.
        preprocessing (bool): preprocess location before matching.
        data_root (str): root directory holding the data.

    Returns:
        str: json representation of the result object.
    """
    locations = pd.Series(locations)
    gov = Gov(data_root)
    gov.load_data()
    gov.build_indices()

    m = Matcher(gov)
    m.get_match_for_locations(locations)

    return m.results


def main():
    args = parse_args()

    if args.location:
        result = get_match(args.location, args.use_preprocessing, args.data_root)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            locations = fh.read().splitlines()
        result = get_matches(locations, args.use_preprocessing, args.data_root)

    pprint.pprint(result)

if __name__ == "__main__":
    main()
