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

# %%
def find_all_items_based_on_types(types:set) -> list[tuple]:
    """
    Given a set of type-ids, the method returns all items having that type.
    The output is presented in a readable fashion.
    Objects may occur twice in the output, if they match 2 or more types of the given type-ids.
    """
    result = []
    for k, v in gov.types_by_id.items():
        for t in types.intersection(v):
            result.append((gov.type_names_by_type[t], v, gov.items_by_id[k][0], gov.names_by_id[k],))
    return sorted(result)


# %% [markdown]
# Print the statistic of how often any type occurs in the GOV class:

# %% tags=[]
from operator import itemgetter

all_type_values = gov.types_by_id.values()
count_by_type = {}

for types in gov.types_by_id.values():
    occurence = 0
    for t in types:
        count_by_type[t] = count_by_type.get(t,0) + 1

count_by_type = dict((k, (v, f"{v/len(all_type_values):.6f}", gov.type_names_by_type[k])) for k,v in count_by_type.items())
    
sorted(count_by_type.items(), key=itemgetter(1), reverse=True)

# %%
len(count_by_type) == len(all_types_found_in_the_paths)

# %% [markdown]
# ### Analyze all types with less than 20 occurences

# %% tags=[]
type_subset = {k for k,v in count_by_type.items() if v[0] <= 20}
find_all_items_based_on_types(type_subset)

# %% [markdown]
# ### Analyze Amt (Kreisähnlich) 78

# %% tags=[]
find_all_items_based_on_types({78})

# %% [markdown]
# ## Choice of T_BEGIN and T_END in class GOV

# %% [markdown]
# ### Kreisreformen im Deutschen Kaiserreich
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Deutschland_bis_1949_(ohne_Bayern_und_Preußen)
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Bayern
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Preußen

# %% [markdown]
# ## give_ids_kreis_or_higher()

# %% tags=[]
high_lvl_items = gov.give_ids_kreis_or_higher()
len(high_lvl_items)

# %%
