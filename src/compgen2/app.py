import argparse
import json
import pprint
import textwrap
from datetime import datetime
from collections import defaultdict

import pandas as pd
import pyperclip as pc

from compgen2.correction import Preprocessing
from compgen2.gov import Gov, Matcher

MATCHER_PARAMS = {
    "use_difflib": True,
    "use_phonetic": True,
    "max_cost": 3,
    "search_kreis_first": True,
}


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
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode to try out the matching algorithm."
    )
    parser.add_argument(
        "-f",
        "--file",
        help="TXT file with location names, one name per line. All locations will be matched against the GOV database.",
    )
    parser.add_argument("-d", "--data-root", required=True, help="Path to the local data root directory.")
    parser.add_argument("-p", "--use-preprocessing", action="store_true")

    return parser.parse_args()


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
    print("Loading GOV...")
    gov = Gov(data_root)
    gov.load_data()
    gov.build_indices()

    if preprocessing:
        print("Preprocessing location names...")
        locations = Preprocessing.replace_characters_vl(locations).str.strip()
        locations = Preprocessing.replace_corrections_vl(locations).str.strip()
        locations = Preprocessing.substitute_partial_words(locations, data_root).str.strip()
        locations = Preprocessing.substitute_delete_words(locations, data_root).str.strip()
        locations = Preprocessing.substitute_full_words(locations, data_root).str.strip()

        old_names = list(gov.ids_by_name.keys())
        new_names = Preprocessing.replace_characters_gov(pd.Series(old_names, dtype=str)).str.strip()
        new_names = Preprocessing.substitute_partial_words(pd.Series(new_names), data_root).str.strip()
        new_names = Preprocessing.substitute_delete_words(pd.Series(new_names), data_root).str.strip()
        new_names = Preprocessing.substitute_full_words(pd.Series(new_names), data_root).str.strip()

        ids_by_pname = defaultdict(set)
        for old_name, new_name in zip(old_names, new_names):
            ids_by_pname[new_name] |= gov.ids_by_name[old_name]
        ids_by_pname.default_factory = None
        gov.ids_by_name = ids_by_pname

        pnames_by_id = defaultdict(set)
        for k, v in ids_by_pname.items():
            for i in v:
                pnames_by_id[i] |= {k}
        pnames_by_id.default_factory = None
        gov.names_by_id = pnames_by_id

    m = Matcher(gov, **MATCHER_PARAMS)
    m.get_match_for_locations(locations)

    return m.results


def interactive_mode(data_root: str):
    print("You have started the interactive mode.")
    print("Please wait while the GOV database is loading...")
    gov = Gov(data_root)
    gov.load_data()
    gov.build_indices()

    while True:
        location_str = input(
            "Please enter the location you want to match against the GOV database. If you want to quit, just enter 'q'.\n"
        )

        if location_str.lower() == "q":
            break

        location = pd.Series([location_str])

        use_preprocessing = input("Do you want to use preprocessing (y|n)?\n")

        if use_preprocessing.lower() == "y":
            location = Preprocessing.replace_characters_vl(location)
            location = Preprocessing.replace_corrections_vl(location)
            location = Preprocessing.substitute_partial_words(location, data_root)
            location = Preprocessing.substitute_delete_words(location, data_root)
            location = Preprocessing.substitute_full_words(location, data_root)

        m = Matcher(gov, **MATCHER_PARAMS)
        m.get_match_for_locations(location)

        print("Here is the result for your query.")
        pprint.pprint(m.results[location[0]])
        
        user_iput = input("Do you want the result to be copied to your clipboard (y|n)?\n")
        if user_iput.lower() == 'y':
            pc.copy(json.dumps(m.results))
        print()


def main():
    args = parse_args()

    if args.interactive:
        interactive_mode(args.data_root)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            locations = fh.read().splitlines()
        print(f"Processing {len(locations)} locations...")
        result = get_matches(locations, args.use_preprocessing, args.data_root)

        output = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_compgen2.json"
        print(f"Results will be written to {output}.")
        with open(output, "w", encoding="utf-8") as fh:
            json.dump(result, fh)


if __name__ == "__main__":
    main()
