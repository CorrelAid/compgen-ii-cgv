# -*- coding: utf-8 -*-
# +
import pickle

import pandas as pd

from compgen2 import GOV, Matcher, GovTestData, Preprocessing_VL

# +
from pathlib import Path

Path(".").cwd()
# -

# !pip install line_profiler

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

data_root= "..data/"

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


