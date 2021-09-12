# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np

# %% [markdown]
# # Read in VL

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
# ## Add regions as columns

# %%
#df_region = verlustliste.location.str.split(",", expand=True)
#df_region.rename(columns={col:f"part_{col}" for col in df_region.columns}, inplace=True)
#df_region = df_region.apply(lambda col: col.str.strip())

#df_region

# %%
#df_region.loc[7]["part_1"]

# %%
#verlustliste = verlustliste.join(df_region)

# %%
#verlustliste

# %%
#(~verlustliste["part_4"].isna()).sum()

# %%
#verlustliste.info()

# %%
#verlustliste["part 1"] = pd.arrays.SparseArray(verlustliste["part 1"])
#verlustliste["part 2"] = pd.arrays.SparseArray(verlustliste["part 2"])
#verlustliste["part 3"] = pd.arrays.SparseArray(verlustliste["part 3"])
#verlustliste["part 4"] = pd.arrays.SparseArray(verlustliste["part 4"])

# %%
#verlustliste.info()

# %% [markdown]
# ## Store as parquet

# %%
verlustliste.to_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %% [markdown]
# ## Read in parquet

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %%
verlustliste

# %%
verlustliste.info()

# %% [markdown]
# # Read in GOV 

# %%
# read in gov data 
gov = pd.read_csv("../data/gov_orte_v01.csv", sep="\t", header=None, names=["id", "location"])

# %%
gov

# %%
gov.info()

# %%
# Add regions as columns?

# %% [markdown]
# ## Store as parquet

# %%
gov.to_parquet("../data/gov_orte_v01.parquet")

# %% [markdown]
# ## Read in parquet

# %%
gov = pd.read_parquet("../data/gov_orte_v01.parquet")

# %% [markdown]
# # Read in gov Kreise

# %%
gov_kreise = pd.read_csv("../data/gov_kreise_v01.csv", sep="\t", header=None, names=["id", "location"])

# %%
gov_kreise

# %%
gov_kreise.info()

# %% [markdown]
# ## Store as parquet

# %%
gov_kreise.to_parquet("../data/gov_kreise_v01.parquet")

# %% [markdown]
# ## Read in parquet

# %%
gov_kreise = pd.read_parquet("../data/gov_orte_v01.parquet")

# %%
