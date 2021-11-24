# -*- coding: utf-8 -*-
# %%
from pathlib import Path
import re

import pandas as pd
import numpy as np

from compgen2 import Gov, Matcher, const, Preprocessing

# %%
# %load_ext autoreload
# %autoreload 2

# %% [markdown]
# # Preprocessing

# %%
data_root = Path("../data")

# %% [markdown]
# ## Verlustliste

# %%
# Lade verlustliste
verlustliste = pd.read_parquet(data_root / const.FILENAME_VL)


# %%
vl = verlustliste.copy()

# %%
vl.location = Preprocessing.replace_corrections_vl(vl.location)
vl

# %%
vl.location = Preprocessing.replace_characters_vl(vl.location)
vl

# %%
# all entries with abbreviations
vl_abbreviations = vl[vl.location.str.contains("[A-Za-zäöüÄÖÜßẞ]+\.")]

# testset
testset = vl_abbreviations.sample(n=30, random_state=299).drop('loc_parts_count', axis=1)
testset

# %%
testset['location_partial'] = Preprocessing.substitute_partial_words(testset['location'], data_root)
testset

# %%
testset['location_delete'] = Preprocessing.substitute_delete_words(testset['location_partial'], data_root)
testset

# %%
testset['location_full'] = Preprocessing.substitute_full_words(testset['location_delete'], data_root)
testset

# %%
testset['location_i']= testset.location_full.replace(to_replace=" i\.", value=",", regex=True)
testset

# %%
