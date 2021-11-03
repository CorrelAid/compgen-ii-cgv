# +
import pickle

import pandas as pd

from compgen2 import GOV, Matcher, GovTestData, Synthetic, get_accuracy
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

gtd.get_test_data()

# +
test_set = gtd.get_test_data()[:200]

m = Matcher(gov)
m.get_match_for_locations((p[0] for p in test_set))
# -

get_accuracy(m.results, test_set)

# +
from pprint import pprint

pprint(m.results)
# -
m.get_match_for_locations(["adligrose"])


m.results["adligrose"]

# ## Synthetic data

syn = Synthetic(gov)
synth_data = syn.create_synthetic_data(size=200)

synth_data[:10]

m = Matcher(gov)
m.get_match_for_locations((p[0] for p in synth_data))

get_accuracy(m.results, synth_data)

# +
from pprint import pprint

pprint(m.results)
# -


