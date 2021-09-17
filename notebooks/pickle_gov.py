import pickle

from compgen2 import GOV


data_root = "../data"

gov = GOV(data_root)
gov.load_data()
gov.build_indices()

with open(data_root + "/gov.pickle", "wb") as stream:
    pickle.dump(gov, stream, pickle.HIGHEST_PROTOCOL)


