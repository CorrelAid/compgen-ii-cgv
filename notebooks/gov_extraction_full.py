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
import pandas as pd
import numpy as np
from compgen2 import GOV
from pathlib import Path

# %%
data_root = "../data"
gov = GOV(data_root)

# %%
paths = gov.build_paths()
paths


# %%
pmax = tuple()
pmin = tuple(range(10))
for p in paths:
    l = len(p)
    if l > len(pmax): pmax = p
    if l < len(pmin): pmin = p

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
