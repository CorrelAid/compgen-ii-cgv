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
# # Showcase Preprocessing

# %%
data_root = Path("../data")

# %% [markdown]
# #### Lade Verlustliste

# %%
# Lade verlustliste
vl = pd.read_parquet(data_root / const.FILENAME_VL)


# %% [markdown]
# #### Kreiere Testset mit typischen Fehlern

# %%
testset = pd.concat([vl[vl.location.str.contains("[A-Za-zäöüÄÖÜßẞ]+\.")].sample(n=12, random_state=10),
                    vl[vl.location.str.contains("kr\.")].sample(n=3, random_state=10),
                    vl[vl.location.str.contains("[\[{(]")].sample(n=5, random_state=10),
                    vl[vl.location.str.contains(" verm.")].sample(n=2, random_state=10),
                    vl[vl.location.str.contains(" nicht")].sample(n=3, random_state=10),
                    vl[vl.location.str.contains("[#^]")].sample(n=2, random_state=10)]).drop(['loc_parts_count', 'loc_count'], axis=1).sample(frac=1, random_state=10).reset_index(drop=True)
testset

# %% [markdown]
# ### Preprocessing Sonderzeichen: 1. Entfernen der Korrekturen

# %% [markdown]
# Function replace_corrections_vl() for removing historical corrections '()[]' and modern-day corrections '{}' and variants
# 1. brackets including their content 
# 2. the word 'nicht' plus related content
# 3. the word 'korrigiert' and its variants plus related content
# 4. the word 'vermutlich' and its variants plus related content

# %%
testset['replace_corrs'] = Preprocessing.replace_corrections_vl(testset.location)
testset

# %% [markdown]
# ### Preprocessing Sonderzeichen: 2. Entfernen weiterer Sonderzeichen

# %% [markdown]
# Function for removing special characters: 
# 1. simply removed: ?^_"#*\:{}()[]!
# 2. replaced with ': ´`

# %%
testset['replace_chars'] = Preprocessing.replace_characters_vl(testset.replace_corrs)
testset

# %% [markdown]
# ### Preprocessing Abkürzungen: 1. Ersetzen allgemeiner Wortendungen

# %% [markdown]
# Function no 1. for substituting abbreviations:
#     
# Flexibly substitutes abbreviations that are part of a longer word (e.g. Seekr./Gebirgskr. -> kreis)

# %%
testset['subst_partial'] = Preprocessing.substitute_partial_words(testset['replace_chars'], data_root)
testset

# %% [markdown]
# ### Preprocessing Abkürzungen: 2. Löschen von nicht benötigten Typeninformationen

# %% [markdown]
# Function no 2. for substituting abbreviations: 
#     
# Removes unnecessary abbreviations and extra words that relates to types (e.g. Kr., Kreis, Amtshauptmannschaft)

# %%
testset['subst_delete'] = Preprocessing.substitute_delete_words(testset['subst_partial'], data_root)
testset

# %% [markdown]
# ### Preprocessing Abkürzungen: 3. Spezifische Ersetzungen

# %% [markdown]
# Function no 3. for substituting abbreviations:
#     
# Substitutes specific abbreviations

# %%
testset['subst_full'] = Preprocessing.substitute_full_words(testset['subst_delete'], data_root)
testset

# %% [markdown]
# ### Optional: " i." (für in) durch Komma ersetzen 
# (Achtung: n+1 Bestandteile)

# %%
testset['subst_i'] = testset.subst_full.replace(to_replace=" i\.", value=",", regex=True)
testset

# %%
