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

# %% [markdown]
# # GOV Auszug

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
# read in gov data 
gov = pd.read_csv("../data/gov_orte_v01.csv", sep="\t", header=None, names=["id", "location"])

# %%
gov.info()

# %%
gov

# %%
gov.sort_values(by=['location'])

# %%
len(set(gov.location)) / len(gov.location) 

# %% [markdown]
# Anmerkung: Es gibt aktuell noch Duplikate/uneindeutige Fälle in gov_orte (nur 65% der Einträge sind eineindeutig). 

# %%
dup_orte = pd.concat(g for _, g in gov.groupby("location") if len(g) > 1)
dup_orte

# %%
# Sonderzeichen

import string
from operator import itemgetter

analysis_special_chars = {}

for char in string.punctuation + '´' + string.digits:
    df_ = gov[gov.location.str.contains(char, regex=False)]
    occurence = len(df_)
    analysis_special_chars[char] = (occurence, occurence / len(gov))
    
sorted(analysis_special_chars.items(), key=itemgetter(1), reverse=True)

# %%
# Beispiele Sonderzeichen

char = "="
gov[gov.location.str.contains(char)]

# %% [markdown]
# Anmerkung: Es gibt Zahlen und Sonderzeichen in gov_orte.

# %% [markdown]
# ## Save as parquet

# %%
gov.to_parquet("../data/gov_orte_v01.parquet")

# %% [markdown]
# ## Load parquet

# %%
gov = pd.read_parquet("../data/gov_orte_v01.parquet")

# %% [markdown]
# # Preprocessing GOV

# %%
# ´ ` und ' vereinheitlichen auf ' 
gov = gov.replace({'location' : { '´' : '\'', '`' : '\''}}, regex=True)

# %%
# Einträgt mit ? ! & + _ * > { } komplett entfernen
chars = ['?', '!', '&', '+', '_', '*', '>', '{', '}', ':']

gov = gov[~gov.location.apply(lambda loc: any(c in loc for c in chars))]
gov

# %%
# TBD: Abkürzungen mit . erweitern?

# %%
# TBD: Übersetzungen mit = getrennt aufsplitten?

# %%
# TBD: Mehrere Bestandteile (v.a. Flüsse oder Regionen) mit , () oder / getrennt aufsplitten?

# %% [markdown]
# ## Save as parquet

# %%
gov.to_parquet("../data/gov_orte_v01_preprocessed.parquet")

# %% [markdown]
# # Load GOV Kreise 

# %%
gov_kreise = pd.read_csv("../data/gov_kreise_v01.csv", sep="\t", header=None, names=["id", "location"])

# %%
gov_kreise

# %%
gov_kreise.info()

# %%
len(set(gov_kreise.location)) / len(gov_kreise.location)

# %% [markdown]
# Anmerkung: Es gibt aktuell noch Duplikate/uneindeutige Fälle in gov_kreise (86% der Einträge sind eineindeutig).

# %%
# Sonderzeichen

sorted(analysis_special_chars.items(), key=itemgetter(1), reverse=True)

# %%
dup_kreise = pd.concat(g for _, g in gov_kreise.groupby("location") if len(g) > 1)
dup_kreise

# %% [markdown]
# ## Save as parquet

# %%
gov_kreise.to_parquet("../data/gov_kreise_v01.parquet")

# %% [markdown]
# ## Load as parquet

# %%
gov_kreise = pd.read_parquet("../data/gov_orte_v01.parquet")

# %%
