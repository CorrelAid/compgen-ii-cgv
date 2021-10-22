# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] tags=[]
# # Kölner Phonetik #43
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/43

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher, const, Phonetic
from pathlib import Path
import sys

# %%
data_root = "../data"
gov = GOV(data_root)

# %% tags=[]
gov.load_data()

# %%
gov.build_indices()

# %% [markdown]
# ## Kölner Phonetik

# %%
ph = Phonetic()

# %%
phonetic_by_name = {}
for n in gov.ids_by_name.keys():
    phonetic_by_name[n] = ph.encode(n)

# %%
len(gov.ids_by_name.keys()), len(set(phonetic_by_name.values()))

# %%
from collections import defaultdict
names_by_phonetic = defaultdict(set)
for k, v in phonetic_by_name.items():
    names_by_phonetic[v] |= {k}
names_by_phonetic.default_factory = None

# %%
list(gov.ids_by_name.keys())[:10]

# %% tags=[]
names_by_phonetic[ph.encode("Düsseldorf")]

# %%
