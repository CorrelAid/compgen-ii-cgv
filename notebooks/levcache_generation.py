import pickle
import pandas as pd
from compgen2 import GOV, Matcher, GovTestData, Preprocessing

# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

data_root= "../data"

gov = GOV(data_root)
gov.load_data()
gov.build_indices()

# + active=""
# with open("../data/gov.pickle", "rb") as stream:
#     gov = pickle.load(stream)
# -

# ## Korrekturliste GOV

gtd = GovTestData(gov)

gtd.data

#valid_test_location = gtd.get_test_locations()
preporcessing_operations = [Preprocessing.prep_clean_brackets, Preprocessing.prep_clean_korrigiert, Preprocessing.prep_clean_korrigiert, Preprocessing.prep_clean_characters]
for pre in preporcessing_operations:
    preprocessed = pre(pd.Series(valid_test_location))
m = Matcher(gov)

m.get_match_for_locations(preprocessed)

# build the dictionary now:)))
# get all parts
listed = list(m.results.values())
partMap = {}
for d in list(map(lambda x: x["parts"], listed)):
    partMap.update(d)
def small_listtodict(list_fullcandidates):
    full_can = {}
    for element in list_fullcandidates:
        if element[1] not in full_can:
            full_can[element[1]] = []
        full_can[element[1]].append(element[0])
    return full_can
cache_dict = {k:small_listtodict(partMap[k]["full_candidates"]) for k in partMap}

# +
import json

with open('test_parts_cache.json', 'w') as fp:
    json.dump(cache_dict, fp)

# +
from pprint import pprint

pprint(m.results)