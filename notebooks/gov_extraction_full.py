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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV
from pathlib import Path

# %%
# does not work in a notebook so replace with path to data root
#data_root = Path(__file__).parent.parent.joinpath("data")
data_root = "/mnt/d/git/compgen-ii-cgv/data"
gov = GOV(data_root)

# %%
paths = gov.build_paths()
paths


# %%
pmax = tuple()
for p in paths:
    l = len(p)
    if l > len(pmax): pmax = p

# %%
pmax

# %%
gov.decode_paths_name({pmax})

# %%
gov.decode_paths_id({pmax})

# %%
