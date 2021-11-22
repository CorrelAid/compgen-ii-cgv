from compgen2 import Synthetic
import pickle

with open("../data/gov.pickle", "rb") as stream:
    gov = pickle.load(stream)

syn = Synthetic(gov)

if __name__ == "__main__":
    syn.create_synthetic_data(size=100)