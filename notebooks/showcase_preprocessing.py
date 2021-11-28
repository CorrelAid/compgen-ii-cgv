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
vl = pd.read_parquet(data_root / const.FILENAME_VL)


# %%
testset = pd.concat([vl[vl.location.str.contains("[A-Za-zäöüÄÖÜßẞ]+\.")].sample(n=12, random_state=10),
                    vl[vl.location.str.contains("kr\.")].sample(n=3, random_state=10),
                    vl[vl.location.str.contains("[\[{(]")].sample(n=5, random_state=10),
                    vl[vl.location.str.contains(" verm.")].sample(n=2, random_state=10),
                    vl[vl.location.str.contains(" nicht")].sample(n=3, random_state=10),
                    vl[vl.location.str.contains("[#^]")].sample(n=2, random_state=10)]).drop(['loc_parts_count', 'loc_count'], axis=1).sample(frac=1, random_state=10).reset_index(drop=True)
testset

# %%
testset['replace_corrs'] = Preprocessing.replace_corrections_vl(testset.location)
testset

# %%
testset['replace_chars'] = Preprocessing.replace_characters_vl(testset.replace_corrs)
testset

# %%
testset['subst_partial'] = Preprocessing.substitute_partial_words(testset['replace_chars'], data_root)
testset

# %%
testset['subst_delete'] = Preprocessing.substitute_delete_words(testset['subst_partial'], data_root)
testset

# %%
testset['subst_full'] = Preprocessing.substitute_full_words(testset['subst_delete'], data_root)
testset

# %%
testset['subst_i'] = testset.subst_full.replace(to_replace=" i\.", value=",", regex=True)
testset

# %%
