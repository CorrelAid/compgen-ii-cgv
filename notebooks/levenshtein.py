from compgen2 import LocCorrection
import Levenshtein

dirs(levenshtein)

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

lC = LocCorrection.from_list(tuple(gov.get_loc_names()))

lC.search("gailingen", 1)

gov.names.content.str.lower().isin(["sagan"]).any()

gov.names.content


