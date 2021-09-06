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
gov = pd.read_parquet("./data/gov_orte_v01.parquet")

# Entferne Duplikate
gov = gov.drop_duplicates(subset='location', keep="first")
gov

# %%
gov_kreise = pd.read_parquet("./data/gov_kreise_v01.parquet")

# Entferne Duplikate 
gov_kreise = gov_kreise.drop_duplicates(subset='location', keep="first")
gov_kreise

# %% [markdown]
# # Load Verlustliste

# %%
verlustliste = pd.read_parquet("./data/deutsche-verlustlisten-1wk.parquet")
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
unmatched = temp_1e[temp_1e['_merge']=='left_only']

# %%
unmatched.head()

# %%
len(unmatched)

# %%
# entries that only contains one word and only cotains alphabets
unmatched_oneword = unmatched.loc[unmatched.location.apply(lambda x: str.isalpha(x))==True]

# %%
len(unmatched_oneword)
print("entries with only alphabets: ", len(unmatched_oneword)/len(unmatched))


# %% [markdown]
# # Levenshtein Distance Check

# %%
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


# %%
unmatched_oneword

# %%
gov_oneword = gov[gov.location.apply(lambda x: len(x.split())==1)]

# %%
gov_oneword.head()

# %%
len(gov_oneword)

# %%
string="aachen"
gov_oneword[(gov_oneword.location.map(len)>=len(string)-2) & (gov_oneword.location.map(len)<=len(string)+2)]


# %%
# goal is to find a location in govlist that has small distance with the unmatched word
def find_per_ld(string, gov_list,distance=1):
    filtered_gov_list = gov_list[(gov_list.location.map(len)>=len(string)-2) & (gov_list.location.map(len)<=len(string)+2)].location.values
    distance_list = list(enumerate(map(lambda x: levenshteinDistance(x, string), filtered_gov_list)))
    filtered_indexes = [i[0] for i in distance_list if i[1]<=distance]
    #print(filtered_indexes)
    return [filtered_gov_list[i] for i in filtered_indexes]


# %%
#unmatched_oneword["matched_results_ld1"] = unmatched_oneword.location.apply(lambda x: ", ".join(find_per_ld(x, gov_oneword, distance=1)))

# %%
unmatched_oneword

# %%
location.apply(lambda x: ", ".join(find_per_ld(x, gov_oneword, distance=1)))
