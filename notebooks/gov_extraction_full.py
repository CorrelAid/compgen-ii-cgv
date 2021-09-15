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
list(gov.all_relations())[:10]

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
gov.decode_paths_name(matcher.find_relevant_paths("Blasdorf, Landeshut"))

# %%
gov.decode_paths_name(matcher.find_relevant_paths("Blasdorf"))

# %%
gov.names.query("content == 'Landeshut'")

# %%
