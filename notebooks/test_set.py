# -*- coding: utf-8 -*-
# +
import pickle

import pandas as pd

from compgen2 import GOV, Matcher, GovTestData, Synthetic
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

# ## Korrekturliste GOV

gtd = GovTestData(gov)

gtd.data

gtd.get_test_locations()

# +
valid_test_location = gtd.get_test_locations()

m = Matcher(gov)
m.get_match_for_locations(valid_test_location[:10])
# -

gtd.get_accuracy(m.results)

# +
from pprint import pprint

pprint(m.results)
# -
m.get_match_for_locations(["Gračanica, Bosnien"])


# +
from pprint import pprint

pprint(m.results["Gračanica, Bosnien"])
# -

# ## Synthetic data

syn = Synthetic(gov)
synth_data = syn.create_synthetic_data(size=100)

synth_data[:10]

# +
test_locations = [pair[1] for pair in synth_data]

m = Matcher(gov)
m.get_match_for_locations(test_locations)
# -

m.results


