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

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher
from pathlib import Path

# %% [markdown]
# ## Using GOV

# %%
data_root = "../data"
gov = GOV(data_root)

# %%
gov.items

# %% tags=[]
gov.names

# %%
gov.types

# %%
gov.type_names

# %%
gov.relations

# %%
paths = gov.all_paths()
list(paths)[:10]


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
gov.get_all_ids_for_name("Krefeld")

# %%
gov.decode_paths_name({gov.get_all_ids_for_name("Krefeld")})

# %%
set().update(gov.get_all_ids_for_name("Krefeld"))

# %% [markdown]
# ## Using Matcher

# %%
matcher = Matcher(gov)

# %% tags=[]
matcher.find_relevant_paths("Blasdorf, Landeshut")

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Blasdorf"))

# %%
gov.names.query("content == 'Landeshut'")

# %%
matcher.find_relevant_paths("Aach, Freudenstadt")

# %%
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Aach, Freudenstadt"), "Aach, Freudenstadt")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Freudenstadt"), "Freudenstadt")

# %%
gov.all_reachable_nodes_by_id()[1279230]

# %% jupyter={"outputs_hidden": true, "source_hidden": true} tags=[]
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %% tags=[] jupyter={"outputs_hidden": true}
gov.decode_paths_name(matcher.find_relevant_paths("Neustadt"))

# %% jupyter={"outputs_hidden": true} tags=[]
matcher.find_relevant_paths("Sachsen")

# %%
