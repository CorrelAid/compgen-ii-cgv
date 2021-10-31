# -*- coding: utf-8 -*-
# +
import pickle

import pandas as pd

from compgen2 import Pipeline, Matcher, GOV, LocCorrection
# -

# !pip install line_profiler

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

# ## Complete Pipeline Run

data_root = "../data"
p = Pipeline(data_root)

p.run()

# +
import pickle

with open(r"D:\git\compgen-ii-cgv\notebooks\log\pipeline\pipeline_v01.pickle", "rb") as stream:
    p = pickle.load(stream)
    
p.run()
# -
# ## Pipeline Profiling

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

m = Matcher(gov)
m.get_match_for_locations(["schönau, attersteg"])

m = Matcher(gov)
m.get_match_for_locations(["Abb. Stolzenberg"])

# +
from pprint import pprint

pprint(m.results)
# -

# %lprun?

p = Pipeline(data_root)
p.load_data()
locations = p.vl.location.sample(200).values.tolist() # random samples
m = Matcher(gov)
# %lprun -s -u 1e-6 -f m.find_parts_for_location -f m.find_textual_id_for_location m.get_match_for_locations(locations)

pprint(m.results)

p = Pipeline(data_root)
p.load_data()
locations = p.vl[p.vl.location.str.count(",") == 0].location.iloc[:5].values.tolist()  # only samples with 1 part
m = Matcher(gov)
# %lprun -s -u 1e-6 -f m.find_parts_for_location -f m.find_textual_id_for_location m.get_match_for_locations(locations)

p = Pipeline(data_root)
p.load_data()
locations = p.vl[p.vl.location.str.count(",") == 1].location.sample(200).values.tolist()  #  only samples w ith 2 parts
m = Matcher(gov)
# %lprun -s -u 1e-6 -f m.find_parts_for_location -f m.find_textual_id_for_location m.get_match_for_locations(locations)

# +
from pprint import pprint

pprint(m.results)
# -

for s in sorted(list(gov.ids_by_name.keys())):
    if s.startswith("alt"):
        print(s)


