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

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %% [markdown]
# # Load GOV Liste

# %%
gov = pd.read_parquet("../data/gov_orte_v01.parquet")

# Entferne Duplikate
gov = gov.drop_duplicates(subset='location', keep="first")
gov

# %%
gov_kreise = pd.read_parquet("../data/gov_kreise_v01.parquet")

# Entferne Duplikate 
gov_kreise = gov_kreise.drop_duplicates(subset='location', keep="first")
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
verlustliste.query("location in @gov.location or location in @gov_kreise.location")

# %%
verlustliste_mit_regionen = verlustliste.location.str.split(",", expand=True)
verlustliste_mit_regionen.columns = ["location", "1","2","3","4"]

# %%
verlustliste_mit_regionen

# %%
gov_all = pd.concat([gov.location, gov_kreise.location])

# %%
gov_all

# %%
# Welche 1. Einträge matchen mit GOV, egal ob mit oder ohne weiteren Bestandteilen
verlustliste_mit_regionen.query("location in @gov_all") 

# %%
len(verlustliste_mit_regionen.query("location in @gov.location or location in @gov_kreise.location")) / len(verlustliste)

# %% [markdown]
# Demnach matchen 44% aller Einträge mit dem GOV, wenn man nur den allerersten Bestandteil nimmt, egal ob danach noch weitere Bestandteile kommen

# %%
verlustliste = verlustliste.append(verlustliste.location.str.split(",", expand=True))

# %%
verlustliste.loc[10]

# %%
verlustliste.iloc[10, 0:5].isin(gov.location)

# %%
matches = []
for loc in verlustliste.location:
    parts = loc.split(",")
    for part in parts:
        if part not in gov.location or part not in gov_kreise.location:
            matches.append("")
            continue
    
    first_part = parts[0]
    if first_part in gov.location:
        matches.append(gov.query("location == @first_part")["id"])
    else:
        matches.append(gov_kreise.query("location == @first_part")["id"])

# %%
matches = pd.Series(matches, index=verlustliste.location)

# %%
