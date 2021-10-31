# +
import pickle

from compgen2 import LocCorrection, Matcher
# -

# %load_ext autoreload
# %autoreload 2

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

lC = LocCorrection.from_list(tuple(gov.get_loc_names()))

# +
candidates = lC.search("alt vahn", 2)

candidates
# -

gov.names.content.str.lower().isin(["sagan"]).any()

gov.names.content

min(candiadtes, key=lambda x: x[1])

# +
from compgen2.const import T_KREISUNDHOEHER, T_STADT

m = Matcher(gov)
lC = LocCorrection.from_list(tuple(m.get_loc_names()))
lC.search("alt vahn", 4)
# -

m = Matcher(gov)
m.get_match_for_locations(["alt vahn, kreis neustettin"])

m.results


