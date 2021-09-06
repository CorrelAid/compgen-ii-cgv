# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %% [markdown]
# # Read in TSV

# %%
verlustliste = pd.read_csv("../data/deutsche-verlustlisten-1wk.tsv", sep="\t", header=None, names=["loc_count", "location"])

# %%
verlustliste

# %% [markdown]
# ## Filter

# %%
verlustliste[verlustliste.location.isna()]

# %%
# filter out one row where location is not available
verlustliste = verlustliste[~verlustliste.location.isna()]

# %%
verlustliste.info()


# %% [markdown]
# ## Add location parts count as feature

# %%
def get_location_parts_count(loc):
    return len(loc.split(","))

verlustliste.location.map(get_location_parts_count)

# %%
verlustliste = verlustliste.assign(loc_parts_count = verlustliste.location.map(get_location_parts_count))

# %%
verlustliste

# %%
verlustliste.query("loc_parts_count in [4,5]")

# %%
verlustliste.info()

# %% [markdown]
# # Store as parquet

# %%
verlustliste.to_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %% [markdown]
# # Read in parquet

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %%
verlustliste

# %%
verlustliste.info()

# %%
