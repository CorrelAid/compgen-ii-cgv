# %%
import pandas as pd
import numpy as np

# %% [markdown]
# # Split verlustliste

# %%
# Lade verlustliste
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk_preprocessed.parquet")

# %%
verlustliste

# %%
# Sonderzeichen , -> Split in einzelne Bestandteile 
verlustliste_mit_regionen = verlustliste.location.str.split(",", expand=True)
verlustliste_mit_regionen.columns = ["location", "1","2","3","4"]

# %%
verlustliste_mit_regionen

# %% [markdown]
# ## Store as parquet

# %%
verlustliste_mit_regionen.to_parquet("../data/deutsche-verlustlisten-1wk_preprocessed_split.parquet")

# %%
