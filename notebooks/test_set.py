# -*- coding: utf-8 -*-
# +
import pickle
from pathlib import Path

import pandas as pd

from compgen2 import GOV, Matcher, GovTestData, Preprocessing_VL
from compgen2.const import VL_FILE

# +
from pathlib import Path

Path(".").cwd()
# -

# !pip install line_profiler

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

data_root= "../data/"

gov = GOV(data_root)
gov.load_data()
gov.build_indices()

# instead of the precious cell you can load a pickled version of gov
with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

# ## Korrekturliste GOV ohne Preprcoessing

gtd = GovTestData(gov)

gtd.data

gtd.get_test_locations()

# +
valid_test_location = gtd.get_test_locations()

m = Matcher(gov)
m.get_match_for_locations(valid_test_location)
# -

gtd.get_accuracy(m.results)

# ## Korrekturliste GOV mit VL Preprcoessing


# +
gtd = GovTestData(gov)
gtd.data["raw"] = Preprocessing_VL.replace_corrections_vl(gtd.data["raw"])
gtd.data["raw"] = Preprocessing_VL.replace_characters_vl(gtd.data["raw"])
#gtd.data["raw"] = Preprocessing_VL.replace_abbreviations_vl(gtd.data["raw"])

valid_test_locations = pd.Series(gtd.get_test_locations())
# -

m = Matcher(gov)
m.get_match_for_locations(valid_test_locations)

gtd.get_accuracy(m.results)


# ## Original VL ohne Preprocessing

def read_vl(data_root) -> pd.DataFrame:
    path = Path(data_root) / VL_FILE
    parquet_filename = path.parent / (
        path.stem + ".parquet"
    )  # replace .csv with .parquet

    def get_location_parts_count(loc):
        return len(loc.split(","))

    # read in tsv and save as parquet, if not already done
    if not Path(parquet_filename).exists():
        vl = pd.read_csv(
            path, sep="\t", header=None, names=["loc_count", "location"]
        )
        vl = vl[~vl.location.isna()]
        vl = vl.assign(loc_parts_count=vl.location.map(get_location_parts_count))
        vl.to_parquet(parquet_filename)

    return pd.read_parquet(parquet_filename)


vl = read_vl(data_root)

vl.sample(10)



performance = []
N = 100
for i in range(10):
    valid_test_locations = vl.location.sample(N)
    valid_test_locations_preprocessed = Preprocessing_VL.replace_corrections_vl(valid_test_locations)
    valid_test_locations_preprocessed = Preprocessing_VL.replace_characters_vl(valid_test_locations_preprocessed)
    
    m_one = Matcher(gov)
    m_one.get_match_for_locations(valid_test_locations)
    
    m_two = Matcher(gov)
    m_two.get_match_for_locations(valid_test_locations_preprocessed)
    
    performance.append(
        (
            len([entry for entry in m_one.results.values() if entry["possible_matches"]]) / N, 
            len([entry for entry in m_two.results.values() if entry["possible_matches"]]) / N
        )
    )
    

performance


