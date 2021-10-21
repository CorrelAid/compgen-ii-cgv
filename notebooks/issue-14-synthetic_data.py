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
# ## Special characters in the GOV (EDA)

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
# ## Decompose string

# %%
def give_type(s:str) -> int:
    if (s in string.punctuation or s in string.whitespace) and s != ".":
        return 2
    elif s == ".":
        return 1
    else:
        return 0
    return 


# %%
def decompose(s:str) -> str:
    l = []
    t_curr = None
    t_prev = None
    for c in s:
        t_curr = give_type(c)
        if t_curr == t_prev:
            l[-1] += c
        else:
            l.append(c)
        t_prev = t_curr
    return l


# %%
decompose("Hallo was ist das. (((genau)))...")

# %% [markdown]
# ## String manipulator 1: Shorten string

# %%
import random
random.seed('compgen')


# %%
def shorten(l:list) -> list:
    sub = [i for i,n in enumerate(l) if len(n) > 1 and give_type(n[0])==0]
    if len(sub) > 0:
        r = random.choice(sub)
        c = random.randint(1,len(l[r])-1)
        l[r] = l[r][0:c]
        if r+1 == len(l) or l[r+1] != ".":
            l.insert(r+1,".")            
    return l


# %%
shorten(decompose('Hallo und guten Tag Michael'))

# %%
"".join(shorten(decompose('(((a b cd.)))')))

# %%
data_shorten = {"".join(shorten(decompose(n))) for n in data}

# %% tags=[] jupyter={"outputs_hidden": true}
data_shorten


# %% [markdown]
# ## String manipulator 2: Drop characters

# %%
def drop(l:list) -> list:
    sub = [i for i,n in enumerate(l) if len(n) > 1 and give_type(n[0])==0]
    if len(sub) > 0:
        r = random.choice(sub)
        c = random.randint(0,len(l[r])-1)
        l[r] = l[r][0:c]+l[r][c+1:]
    return l


# %%
drop(decompose('Hallo und guten Tag Michael'))

# %%
s = decompose("""Very nicely written. In addition, the example chosen was itself lovely to play with.""")
for i in range(5):
    s = shorten(drop(s))
"".join(s)

# %% [markdown]
# ## String manipulator 3: Phonetic distortion

# %% [markdown]
# ### Kölner Phonetik

# %%
import collections
import re


RULES = collections.OrderedDict()
RULES[re.compile(r".[AEIJOUYÄÖÜ].", re.I)]    = "0"
RULES[re.compile(r".[B].", re.I)]             = "1"
RULES[re.compile(r".[P][^H]", re.I)]          = "1"
RULES[re.compile(r".[DT][^CSZ]", re.I)]       = "2"
RULES[re.compile(r".[FVW].", re.I)]           = "3"
RULES[re.compile(r".[P][H]", re.I)]           = "3"
RULES[re.compile(r".[GKQ].", re.I)]           = "4"
RULES[re.compile(r"\s[C][AHKLOQRUX]", re.I)]  = "4"
RULES[re.compile(r"[^SZ][C][AHKOQUX]", re.I)] = "4"
RULES[re.compile(r"[^CKQ][X].", re.I)]        = "48"
RULES[re.compile(r".[L].", re.I)]             = "5"
RULES[re.compile(r".[MN].", re.I)]            = "6"
RULES[re.compile(r".[R].", re.I)]             = "7"
RULES[re.compile(r".[SZß].", re.I)]           = "8"
RULES[re.compile(r"[SZ][C].", re.I)]          = "8"
RULES[re.compile(r"\s[C][^AHKLOQRUX]", re.I)] = "8"
RULES[re.compile(r"[C][^AHKOQUX]", re.I)]     = "8"
RULES[re.compile(r".[DT][CSZ]", re.I)]        = "8"
RULES[re.compile(r"[CKQ][X].", re.I)]         = "8"

SPECIAL_CHARACTER = re.compile(r"[^a-zäöüß\s]", re.I)


def encode(inputstring):  # type: (str) -> str
    """
    encode(string inputstring) -> string
      Returns the phonetic code of given inputstring.
    """

    # remove anything except characters and whitespace
    inputstring = SPECIAL_CHARACTER.sub("", inputstring)

    encoded = ""
    for i in range(len(inputstring)):
        part = inputstring[i-1 : i+2]
        # The RULES always expect 3 characters. Hence the first and the last character of the string get extendend by a space.
        if len(inputstring) == 1:
            part = f" {inputstring[0]} "
        elif i == 0:
            part = f" {inputstring[:2]}"
        elif i == len(inputstring) - 1:
            part = f"{inputstring[i - 1:]} "

        for rule, code in RULES.items():
            if rule.match(part):
                encoded += code
                break

    # remove immediately repeated occurrences of phonetic codes
    while [v for v in RULES.values() if encoded.find(v*2) != -1]:
        for v in RULES.values():
            encoded = encoded.replace(v*2, v)

    if encoded:
        encoded = encoded[0] + encoded[1:].replace("0", "")

    return encoded

# %% [markdown]
# ## String manipulator 4: Linotype typing errors

# %%

# %%

# %% [markdown]
# ## String manipulator 5: Fractal reading confusion errors

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

