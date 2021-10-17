# -*- coding: utf-8 -*-
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
# # EDA Kreise #35
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/35

# %%
# %load_ext autoreload
# %autoreload 2
# #%load_ext memory_profiler
# #%load_ext line_profiler

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher, const
from pathlib import Path
import sys

# %% [markdown]
# ## Initializing GOV instance

# %%
data_root = "../data"
gov = GOV(data_root)

# %% tags=[]
gov.load_data()

# %%
gov.build_indices()

# %% [markdown]
# ## Key figures

# %%
len(gov.all_paths)

# %%
all_types_found_in_the_paths = set().union(*gov.types_by_id.values())
len(all_types_found_in_the_paths)

# %% [markdown]
# ## Analyze types

# %% tags=[]
from operator import itemgetter

data = gov.types_by_id.values()
analysis_types = {}

for types in gov.types_by_id.values():
    occurence = 0
    for t in types:
        analysis_types[t] = analysis_types.get(t,0) + 1

analysis_types = dict((k, (v, f"{v/len(data):.6f}", gov.type_names_by_type[k])) for k,v in analysis_types.items())
    
sorted(analysis_types.items(), key=itemgetter(1), reverse=True)

# %%
len(data)

# %%
len(analysis_types)


# %%
def give_all_type_instances(types:set):
    result = []
    for k, v in gov.types_by_id.items():
        for t in types.intersection(v):
            result.append((gov.type_names_by_type[t], v, gov.items_by_id[k][0], gov.names_by_id[k],))
    return sorted(result)


# %%
type_subset = {k for k,v in analysis_types.items() if v[0] <= 20}

# %% tags=[]
give_all_type_instances(type_subset)

# %% [raw]
# len(analysis_types)

# %% [markdown]
# ### Analyze Amt (Kreisähnlich)

# %% tags=[] jupyter={"outputs_hidden": true}
give_all_type_instances({78})

# %% [markdown]
# ## Choice of T_BEGIN and T_END in class GOV

# %% [markdown]
# ### Kreisreformen im Deutschen Kaiserreich
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Deutschland_bis_1949_(ohne_Bayern_und_Preußen)
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Bayern
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Preußen

# %% [markdown]
# ## "Kreis-Method"

# %% tags=[]
len(gov.give_ids_kreis_or_higher())

# %% tags=[]
gov.ids_by_type[KREISUNDHOEHER]

# %% tags=[]
gov.decode_paths_name({tuple(gov.ids_by_type[64])})

# %%
