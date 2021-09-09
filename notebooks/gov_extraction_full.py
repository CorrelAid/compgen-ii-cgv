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
import gov_extraction as gc

# %%
paths = gc.filter_paths(gc.build_paths())

# %%
pmax = tuple()
for p in paths:
    l = len(p)
    if l > len(pmax): pmax = p

# %%
pmax

# %%
gc.decode_paths_name({pmax})

# %%
gc.decode_paths_id({pmax})

# %%
