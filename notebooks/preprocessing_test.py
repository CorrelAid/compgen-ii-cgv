# -*- coding: utf-8 -*-
# %%
import pandas as pd
import numpy as np
import re
from compgen2 import GOV, Matcher, const, Preprocessing

# %% [markdown]
# # Preprocessing

# %% [markdown]
# ## Verlustliste

# %%
# Lade verlustliste
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")


# %%
vl = verlustliste.copy()

# %%
vl = Preprocessing.replace_corrections_vl(vl)
vl

# %%
vl = Preprocessing.replace_characters_vl(vl)
vl

# %%
# This step is important!
vl["location"] = vl["location"].str.lower()  
vl 

# %%
# all entries with abbreviations
with_abbreviations = vl[vl.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()

# testset
testset = with_abbreviations.sample(n=20, random_state=99).drop('loc_parts_count', axis=1)
testset

# %%
testset['location_partial'] = Preprocessing.substitute_partial_words(testset['location'])
testset

# %%
testset['location_delete'] = Preprocessing.substitute_delete_words(testset['location_partial'])
testset

# %%
testset['location_full'] = Preprocessing.substitute_full_words(testset['location_delete'])
testset

# %%
testset['location_i']= testset.location_full.replace(to_replace=" i\.", value=",", regex=True)
testset

# %%

# %%
