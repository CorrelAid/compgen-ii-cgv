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
# %load_ext line_profiler

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher
from pathlib import Path
import sys

# %% [markdown]
# ## Using GOV

# %%
data_root = "../data"
gov = GOV(data_root)


# %%
def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


# %%
get_size(gov)

# %%
1791218489 / 1024**2

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
paths = gov.all_paths
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
# %lprun -f matcher.find_relevant_ids  matcher.find_relevant_ids("Aach, Freudenstadt")

# %%
# %timeit gov.ids_by_name["Aach"]

# %%
matcher.find_relevant_ids("Freudenstadt")

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Aach, Freudenstadt"))

# %%
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Aach, Freudenstadt"), "Aach, Freudenstadt")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Freudenstadt"), "Freudenstadt")

# %%
gov.all_reachable_nodes_by_id[1279230]

# %% jupyter={"outputs_hidden": true, "source_hidden": true} tags=[]
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %% tags=[] jupyter={"outputs_hidden": true}
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %%
matcher.find_relevant_ids("Neustadt, Sachsen")

# %%

# %%
