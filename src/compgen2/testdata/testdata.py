import logging
from pathlib import Path

import pandas as pd

from ..gov import Gov, Matcher

GOV_URL = "http://wiki-de.genealogy.net/Verlustlisten_Erster_Weltkrieg/Projekt/Ortsnamen"
logger = logging.getLogger(__name__)

class GovTestData:
    def __init__(self, gov: Gov, url: str = GOV_URL):
        self.gov_url = url
        self.gov = gov
        self.filename = "gov_test_data.parquet"
        self.filepath = Path(gov.data_root)

        # load data
        self.data = self.load_gov_test_data()

    def load_gov_test_data(self) -> pd.DataFrame:
        if not (self.filepath / self.filename).exists():
            correction_tables = []
            correction_tables.extend(pd.read_html(self.gov_url, attrs={"class": "sortable"}))
            correction_tables.extend(pd.read_html(self.gov_url, attrs={"class": "wikitable"}))

            df = pd.concat(correction_tables)
            df.columns = ["page", "raw", "corrected"]
            df = df.dropna()

            df = df[~df.raw.str.contains("?", regex=False) & ~df.corrected.str.contains("?", regex=False)]
            df = df.drop(columns=["page"])
            df.to_parquet(self.filepath / self.filename)
        else:
            df = pd.read_parquet(self.filepath / self.filename)

        return df

    def get_test_set(self) -> pd.DataFrame:
        test_set = {"location": [], "truth": []}
        for location, truth in zip(self.data["raw"].str.lower(), self.data["corrected"].str.lower()):
            parts = Matcher.get_query_parts(truth)
            if all(part in self.gov.ids_by_name for part in parts):
                test_set["location"].append(location)
                test_set["truth"].append(truth)
            else:
                logger.debug(f"Could not find {truth} with parts {parts} in GOV.")

        logger.info(f"Found {len(test_set)} valid corrected names in GOV")
        return pd.DataFrame(test_set)


def get_accuracy(results: dict, test_set: pd.DataFrame) -> float:
    """Calculates accuracy for matcher results compared against a ground truth.

    Args:
        results (dict): Output from `matcher.get_match_for_locations`.
        truth (list[str]): A list of expected locations names in the same order as the test set.

    Returns:
        float: Accuracy for test set. A match is counted as correct, if all parts of the truth location can be found in the match.
    """
    correct = 0

    for _, (location, truth) in test_set.iterrows():
        prediction = results.get(location)

        if prediction is not None:
            for match in prediction["possible_matches"]:
                if all(part.strip().lower() in match for part in truth.split(",")):
                    correct += 1
                    break
            else:
                logger.debug(f"Could not solve {location}, expected {truth.lower()}.")
        else:
            logger.error(f"No prediction found for {location}.")

    logger.info(f"Solved {correct} of {len(test_set)} ({correct / len(test_set)}) locations.")
    return correct / len(test_set)
