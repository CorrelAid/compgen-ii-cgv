from compgen2 import Pipeline

# ## Basic Pipeline

data_root = "../data"
p = Pipeline(data_root)

p.run()

# +
import pickle

with open(r"D:\git\compgen-ii-cgv\notebooks\log\pipeline\pipeline_v01.pickle", "rb") as stream:
    p = pickle.load(stream)
    
p.run()
# -


