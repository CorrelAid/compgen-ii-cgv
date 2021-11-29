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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Complete GOV extract #10
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/10

# %%
# %load_ext autoreload
# %autoreload 2
# #%load_ext memory_profiler
# #%load_ext line_profiler

# %%
import pandas as pd
import numpy as np
from compgen2 import Gov, Matcher, const
from pathlib import Path
import sys

# %% [markdown]
# ## Initializing GOV instance

# %%
data_root = "../data"
gov = Gov(data_root)

# %% tags=[]
gov.load_data()

# %%
gov.build_indices()

# %%
#gov.clear_data() # needed when pickled in pipeline

# %% [markdown] tags=[]
# ### Attributes

# %%
for attr in ["items", "names", "types", "relations", "type_names"]:
    print(f"Data: {attr}")
    print(getattr(gov, attr).head())

# %%
# all paths are accessible via all_paths attribute
paths = gov.all_paths
list(paths)[:10]


# %% tags=[] jupyter={"outputs_hidden": true}
gov.items_by_id

# %% tags=[] jupyter={"outputs_hidden": true}
gov.names_by_id

# %% tags=[] jupyter={"outputs_hidden": true}
gov.ids_by_name

# %% tags=[] jupyter={"outputs_hidden": true}
gov.types_by_id

# %% tags=[] jupyter={"outputs_hidden": true}
gov.all_reachable_nodes_by_id

# %% [markdown] tags=[]
# ## Using GOV instance

# %%
pmax = max(paths, key=lambda p: len(p))
pmin = min(paths, key=lambda p: len(p))

# %%
pmax, pmin

# %%
gov.decode_path_name(pmax)

# %%
gov.decode_path_id(pmax)

# %%
gov.names_by_id[190315]

# %%
gov.decode_path_type(pmax)

# %%
gov.decode_path_name(pmin)

# %%
gov.decode_path_id(pmin)

# %%
gov.decode_path_type(pmin)

# %%
gov.ids_by_name["krefeld"]

# %%
gov.decode_path_name(tuple(gov.ids_by_name["krefeld"]))

# %% [markdown]
# ## Using Matcher

# %%
matcher = Matcher(gov)

# %%
matcher.get_match_for_locations(["Blasdorf, Landeshut"])

# %%
matcher.results

# %% [markdown]
# ## Weitere Beispiele

# %% tags=[]
matcher.get_match_for_locations("Aach, Freudenstadt")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.results

# %% tags=[]
matcher.get_match_for_locations("Neustadt, Sachsen")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.results
