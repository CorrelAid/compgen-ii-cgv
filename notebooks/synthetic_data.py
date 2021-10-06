# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Synthetical data #14
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/14

# %%
import pandas as pd
from compgen2 import GOV, Matcher, const

# %%
data_root = "../data"
gov = GOV(data_root)

# %% tags=[]
gov.load_data()

# %% tags=[]
gov.build_indices()

# %% [markdown]
# ## EDA (small) of GOV

# %%
data = gov.ids_by_name.keys()

# %%
# Code von Michael aus data_exploration 

import string
from operator import itemgetter

analysis_special_chars = {}

for char in string.punctuation + '´' + string.digits:
    occurence = 0
    for n in data:
        if n.find(char) > 0: occurence +=1
        analysis_special_chars[char] = (occurence, occurence / len(data))
    
sorted(analysis_special_chars.items(), key=itemgetter(1), reverse=True)

# %% [markdown]
# ## Synthetic data

# %%
'Hallo'[0:1]


# %%
def is_undesired(s:str) -> bool:
    return (s in string.punctuation or s in string.whitespace) and s != "."


# %%
def split_mod(s:str) -> str:
    l = []
    u_curr = None
    u_prev = None
    for c in s:
        u_curr = is_undesired(c)
        if u_curr == u_prev:
            l[-1] += c
        else:
            l.append(c)
        u_prev = u_curr
    return l


# %%
split_mod("Hallo was ist das. (((genau)))")

# %%
import random
random.seed('compgen')
def shorten(s:str) -> str:
    l = split_mod(s)
    sub = [i for i,n in enumerate(l) if len(n) > 1 and not undesired(n[0])]
    if len(sub) > 0:
        r = random.choice(sub)
        l[r] = l[r][0:random.randint(1,len(l[r])-1)] + '.'
    return "".join(l)


# %%
shorten('Hallo und guten Tag Michael')

# %%
shorten('(((a b cd.)))')

# %%
data_shorten = {shorten(n) for n in data}

# %%
data_shorten

# %%

# %%

# %%
# Abkürzungen
# St. -> Sankt
# b. -> bei
# O.S. -> Oberschlesien
# a./ -> an der
# i. Pr. -> in Preußen
# Herzugtum -> ['Hgt', 'Hzt', 'Hzgt', 'Hzgtm', 'Hrzg', 'Hrzgt', 'Herz', 'H']
# Großherzogtum -> ['Großh'

