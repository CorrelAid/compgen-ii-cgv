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

# %% [markdown] tags=[]
# ## Type statistics

# %% [markdown]
# Print the statistic of how often any type occurs in the GOV class:

# %% tags=[]
count_by_type = gov.type_statistic(return_dict = True)

# %%
len(count_by_type) == len(all_types_found_in_the_paths)


# %% [markdown]
# ### Analyze all types with less than 20 occurences

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
    for o in sorted(result):
        print(o)


# %% tags=[]
type_subset = {k for k,v in count_by_type.items() if v[0] <= 20}
find_all_items_based_on_types(type_subset)

# %% [markdown] tags=[]
# ### Analyze Amt (Kreisähnlich) 78

# %% tags=[] jupyter={"outputs_hidden": true}
find_all_items_based_on_types({78})

# %% [markdown]
# ## Choice of T_BEGIN and T_END in class GOV

# %% [markdown]
# ### Kreisreformen im Deutschen Kaiserreich
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Deutschland_bis_1949_(ohne_Bayern_und_Preußen)
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Bayern
# * https://de.wikipedia.org/wiki/Kreisreformen_in_Preußen

# %% [markdown]
# ## Type hierarchies

# %% [markdown]
# ### Kreis oder höher

# %%
gov.type_statistic(const.T_KREISUNDHOEHER)

# %% tags=[]
ids_kreis_or_higher = gov.get_ids_by_types(const.T_KREISUNDHOEHER)
len(ids_kreis_or_higher)

# %% [markdown]
# ### Städte

# %%
gov.type_statistic(const.T_STADT)

# %%
ids_stadt = gov.get_ids_by_types(const.T_STADT)
len(ids_stadt)

# %% [markdown]
# Gibt es noch etwas zwischen den Kreisen und den Städten?

# %%
from collections import defaultdict
diff_dict = defaultdict(set)
for p in gov.all_paths:
    max_kreis = (0,0)
    min_stadt = (-1,0)
    for i, o in enumerate(p):
        t = gov.types_by_id[o]
        if t & const.T_KREISUNDHOEHER:
            max_kreis = (i, o)
        elif t & const.T_STADT and min_stadt[0] < 0:
            min_stadt = (i, o)
        if min_stadt[0] >= 0:
            diff_dict[max_kreis[0]-min_stadt[0]] |= {(max_kreis[1], min_stadt[1], )}

# %%
diff_dict.keys()

# %%
gov.decode_paths_id(diff_dict[1])

# %%
