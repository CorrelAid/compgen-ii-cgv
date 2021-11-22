from pathlib import Path

import pandas as pd
from compgen2 import GOV, Matcher

GOV_URL = "http://wiki-de.genealogy.net/Verlustlisten_Erster_Weltkrieg/Projekt/Ortsnamen"


class GovTestData:
    def __init__(self, gov: GOV, url: str = GOV_URL):
        self.gov_url = url
        self.gov = gov
        self.filename = "gov_test_data.parquet"
        self.filepath = Path("../data")
        
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
            df.to_parquet("../data/gov_test_data.parquet")
        else:
            df = pd.read_parquet(self.filepath / self.filename)

        return df

    def get_test_data(self) -> list[tuple[str, str]]:
        valid_entries = []
        for location, truth in zip(self.data["raw"].str.lower(), self.data["corrected"].str.lower()):
            parts = Matcher.get_query_parts(truth)
            if all(part in self.gov.ids_by_name for part in parts):
                valid_entries.append((location, truth))
            else:
                print(f"Could not find {truth} with parts {parts} in GOV.")

        print(f"Found {len(valid_entries)} valid corrected names in GOV")
        return valid_entries
    
    
def get_accuracy(results: dict, test_set: list[tuple[str,str]]) -> float:
    """Calculates accuracy for matcher results compared against a ground truth.

    Args:
        results (dict): Output from `matcher.get_match_for_locations`.
        truth (list[str]): A list of expected locations names in the same order as the test set.

    Returns:
        float: Accuracy for test set. A match is counted as correct, if all parts of the truth location can be found in the match.
    """
    correct = 0
    
    for location, truth in test_set:
        prediction = results.get(location)
        
        if prediction is not None:
            for match in prediction["possible_matches"]:
                if all(part.strip().lower() in match for part in truth.split(",")):
                    correct += 1
                    break
            else:
                print(f"Could not solve {location}, expected {truth.lower()}.") 
        else:
            print(f"No prediction found for {location}.")
            
    print(f"Solved {correct} of {len(results)} ({correct / len(results)}) locations.")
    return correct / len(results)
