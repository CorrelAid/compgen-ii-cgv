# +
import pickle
import pandas as pd

from compgen2 import GOV, Matcher
# -

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

data_root= "../data"

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

# ## Tests

# Test with 100% valid data, so all entries should find a match

matcher = Matcher(gov)
test_data = build_test_set(gov, size=1000, num_parts=2, valid=1)

# ## Korrekturliste GOV

df_filtered = pd.read_parquet("../data/gov_test_data.parquet")

matcher = Matcher(gov)


def get_valid_test_locations(df):
    valid_entries = []
    for location, truth in zip(df["raw"].str.lower(), df["corrected"].str.lower()):
        parts = Matcher.get_query_parts(truth)
        if all(part in gov.ids_by_name for part in parts):
            valid_entries.append(location)
        else:
            print(f"Could not find {truth} with parts {parts} in GOV.")
    
    print(f"Found {len(valid_entries)} valid corrected names in GOV")
    return valid_entries


valid_test_location = get_valid_test_locations(df_filtered)

m = Matcher(gov)
m.get_match_for_locations(test_locations)


def get_accuracy(results: dict, df):
    correct = 0
    for location, entry in results.items():
        truth = df[df["raw"].str.lower().eq(location)]["corrected"].values[0]
        for match in entry["possible_matches"]:
            if all(part.strip().lower() in match["parts"] for part in truth.split(",")):
                correct += 1
                break
        else:
            print(f"Could not solve {location}, expected {truth.lower()}.")   
            
    print(f"Solved {correct} of {len(test_locations)} ({correct / len(test_locations)}) locations.")
    return correct / len(test_locations)


get_accuracy(valid_test_location, df_filtered)

# +
from pprint import pprint

pprint(m.results)
# -


