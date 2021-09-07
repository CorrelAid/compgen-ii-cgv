# -*- coding: utf-8 -*-
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

# %% [markdown]
# # Load GOV Liste

# %%
gov = pd.read_parquet("../data/gov_orte_v01.parquet")

# Entferne Duplikate
#gov = gov.drop_duplicates(subset='location', keep="first")
gov

# %%
gov_kreise = pd.read_parquet("../data/gov_kreise_v01.parquet")

# Entferne Duplikate 
#gov_kreise = gov_kreise.drop_duplicates(subset='location', keep="first")
gov_kreise

# %% [markdown]
# # Load Verlustliste

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")
# change to expandierte-abk. sobald Fehler in expandierte-abk von Flo gelöst

# %%
verlustliste.loc[10]

# %%
verlustliste.info()

# %% [markdown]
# # Einfaches Matching der Orte

# %%
# Spezifisches GOV element in Verlustliste
verlustliste.query("location == @gov.location[0]")

# %%
# Spezifisches Verlustliste element in GOV
gov.query("location == @verlustliste.location[0]")

# %% [markdown]
# ### Baseline Matching der Orte mit 1 Bestandteil

# %%
verlustliste_1e = verlustliste.query("loc_parts_count == 1")

# %%
# michael: Lösung mit query ohne merge, falls man die gemergten Ergebnisse nicht braucht
verlustliste.query("loc_parts_count == 1 & location in @gov.location") # 55k Einträge können wir mit gov matchen

# %%
temp_1e = pd.merge(verlustliste_1e, gov, on=["location"], how="outer", indicator=True)

# %%
# Show merged
merged_1e=temp_1e[temp_1e['_merge']=='both']
merged_1e.sort_values(by=['location'])

# %%
len(merged_1e) / len(verlustliste_1e)

# 25% direkte Matches bei Einträgen mit 1 Bestandteil

# %%
len(merged_1e) / len(verlustliste)

# Dies macht allerdings nur einen Bruchteil in der gesamten Verlustliste aus

# %%
# Show not merged
rest_1e=temp_1e[temp_1e['_merge']=='left_only']
rest_1e.sort_values(by=['location'])

# %% [markdown]
# ### Baseline Matching der Orte mit 2 Bestandteile

# %%
verlustliste_2e = verlustliste.query("loc_parts_count == 2")
verlustliste_2e = verlustliste_2e.assign(region=verlustliste_2e.location.str.split(",", expand=True)[1])
verlustliste_2e

# %%
# Verwende gov_kreise
temp_2e = pd.merge(verlustliste_2e, gov_kreise, left_on=['region'], right_on=['location'], how="outer", indicator=True)

# %%
# Show merged
merged_2e=temp_2e[temp_2e['_merge']=='both']
merged_2e.sort_values(by=['region'])

# %%
len(merged_2e) / len(verlustliste_2e)

# Nur sehr geringer Anteil an direkten Matches von GOV Kreise und Orten mit 2 Bestandteilen 

# %%
len(merged_2e) / len(verlustliste)

# %%
# Show not merged
rest_2e=temp_2e[temp_2e['_merge']=='left_only']
rest_2e.sort_values(by=['region'])

# %% [markdown]
# ## match verlustliste gegen gov und gov_kreise

# %%
matches = verlustliste[[f"part_{i}" for i in range(5)]].apply(lambda col: col.isin(gov.location) | col.isin(gov_kreise.location) | col.isna(), axis=0)

matches

# %% [markdown]
# Annahme: Eine einfache Basline ist dann erfüllt, wenn wir alle Bestandteile mit dem GOV matchen. Es ist zwar dann noch nicht die eindeutige ID ermittelt aber alle Bestandteile kommen vor so dass es prinzipiell möglich sein sollte die ID herauszufinden.

# %%
matches.all(axis=1)

# %%
verlustliste.query("loc_parts_count == 2")

# %%
matches.loc[7]

# %%
verlustliste.loc[7]["part_1"]

# %%
gov[gov.location.str.contains("Hadersleben")]

# %%
gov_kreise[gov_kreise.location.str.contains("Hadersleben")]

# %%
