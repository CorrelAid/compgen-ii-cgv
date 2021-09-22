# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3.9 (compgen2)
#     language: python
#     name: compgen2
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
from compgen2 import GOV, Matcher
from pathlib import Path
import sys

# %% [markdown]
# ## Initializing GOV instance

# %%
data_root = "../data"
gov = GOV(data_root)

# %%
gov.load_data()

# %%
gov.build_indices()

# %%
#gov.clear_data() # needed when pickled in pipeline

# %% [markdown]
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

# %% jupyter={"outputs_hidden": true} tags=[]
gov.names_by_id

# %% jupyter={"outputs_hidden": true} tags=[]
gov.ids_by_name

# %% jupyter={"outputs_hidden": true} tags=[]
gov.types_by_id

# %% jupyter={"outputs_hidden": true} tags=[]
gov.all_relations

# %% jupyter={"outputs_hidden": true} tags=[]
gov.all_paths

# %% jupyter={"outputs_hidden": true} tags=[]
gov.all_reachable_nodes_by_id

# %% [markdown]
# ## Using GOV instance

# %%
pmax = max(paths, key=lambda p: len(p))
pmin = min(paths, key=lambda p: len(p))

# %%
pmax, pmin

# %%
gov.decode_paths_name({pmax})

# %%
gov.decode_paths_id({pmax})

# %%
gov.decode_paths_type({pmax})

# %%
gov.decode_paths_name({pmin})

# %%
gov.decode_paths_id({pmin})

# %%
gov.decode_paths_type({pmin})

# %%
gov.extract_all_types_from_paths({pmax})

# %%
gov.ids_by_name["Krefeld"]

# %%
gov.decode_paths_name({tuple(gov.ids_by_name["Krefeld"])})

# %% [markdown]
# ## Using Matcher

# %%
matcher = Matcher(gov)

# %% tags=[]
matcher.find_relevant_paths("Blasdorf, Landeshut")

# %%
matcher.find_relevant_ids("Blasdorf")

# %%
matcher.find_relevant_ids("Blasdorf, Landeshut")

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Blasdorf, Landeshut"))

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Blasdorf"))

# %%
gov.ids_by_name["Landshut"]

# %%
# %lprun -f matcher.find_relevant_paths  matcher.find_relevant_paths("Aach, Freudenstadt")

# %%
# with this command you can measure the runtime of each line in the function
# # %lprun -f matcher.find_relevant_ids  matcher.find_relevant_ids("Aach, Freudenstadt")

# %% [markdown]
# ## Weitere Beispiele

# %%
matcher.find_relevant_ids("Freudenstadt")

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Aach, Freudenstadt"))

# %%
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Aach, Freudenstadt"), "Aach, Freudenstadt")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Freudenstadt"), "Freudenstadt")

# %% jupyter={"outputs_hidden": true} tags=[]
gov.all_reachable_nodes_by_id[1279230]

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %% tags=[]
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %%
matcher.find_relevant_ids("Neustadt, Sachsen")

# %%

# %%
