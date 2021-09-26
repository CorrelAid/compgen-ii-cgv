from compgen2 import Pipeline, Baseline

# ## Basic Pipeline

data_root = "../data"
p = Pipeline(data_root)

p.run()

# +
import pickle

with open(r"D:\git\compgen-ii-cgv\notebooks\log\pipeline\pipeline_v04.pickle", "rb") as stream:
    p = pickle.load(stream)
    
p.run()
# -

# ## Baseline Pipeline

data_root = "../data"
b = Baseline(data_root)

b.run()



# ## Synthetic Test Pipelines

from compgen2.synthetic import TestGOV

TestGOV("../data").run()


