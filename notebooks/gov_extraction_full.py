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

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher
from pathlib import Path

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

# %% tags=[] jupyter={"outputs_hidden": true}
gov.all_paths()

# %% tags=[]
from dataclasses import dataclass, field

@dataclass(frozen=True)
class GOVItem:
    """Class for working with GOV items."""
    id: int
    textual_id: str
    names: set[str] = field(compare=False)
    types: set[str] = field(compare=False)
    type_ids: set[int] = field(compare=False, repr=False)
    children: set[int] = field(compare=False, repr=False)
    parents: set[int] = field(compare=False, repr=False)
    paths: set[tuple[int, ...]] = field(compare=False, repr=False)


ids = gov.names.id.unique()
gov_items = {}

for id_ in ids:
    textual_id = gov.items.query("id == @id_").textual_id.values[0]
    item_names = set(gov.names.query("id == @id_").content)
        
    type_ids = set(gov.types.query("id == @id_").content)
    item_type_ids = type_ids
    
    type_names = set()
    for type_id in type_ids:
        type_names.update(gov.type_names.loc[type_id])
    item_type_names = type_names
    
    item_parents = set(gov.relations.query("child == @id_").parent)
    item_children = set(gov.relations.query("parent == @id_").child)
    
    item_paths = set()
    for path in gov.all_paths():
        if id_ in path:
            item_paths.add(path)
             
    gov_item = GOVItem(
        id_,
        textual_id,
        item_names,
        item_type_names,
        item_type_ids, 
        item_children,
        item_parents,
        item_paths
    )
    
    print(gov_item) 
    print(gov_item.children)
    print(gov_item.parents)
    print(gov_item.paths)
    
    

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

# %%
matcher = Matcher(gov)

# %%
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

# %% jupyter={"outputs_hidden": true} tags=[]
matcher.group_relevant_paths_by_query(matcher.find_relevant_paths("Neustadt, Sachsen"), "Neustadt, Sachsen")

# %% tags=[] jupyter={"outputs_hidden": true}
gov.decode_paths_name(matcher.find_relevant_paths("Neustadt"))

# %%
