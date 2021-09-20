from compgen2 import Pipeline, Baseline

# %load_ext autoreload
# %autoreload 2

data_root = "../data"
p = Pipeline(data_root)

p.run()

b = Baseline(data_root)

b.run()


