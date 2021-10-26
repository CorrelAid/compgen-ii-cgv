# +
import pickle

import pandas as pd

from compgen2 import GOV, Matcher, GovTestData
# -

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

data_root= "../data"

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

# ## Korrekturliste GOV

gtd = GovTestData(gov)

gtd.data

gtd.get_test_locations()

# +
valid_test_location = gtd.get_test_locations()

m = Matcher(gov)
m.get_match_for_locations(valid_test_location[:100])
# -

gtd.get_accuracy(m.results)

# +
from pprint import pprint

pprint(m.results)
# -
m.get_match_for_locations(["adligrose"])


m.results["adligrose"]


