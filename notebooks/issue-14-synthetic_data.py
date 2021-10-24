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
import numpy as np

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
def type_code(s:str) -> int:
    if (s in string.punctuation or s in string.whitespace) and s != ".":
        return "punct"
    elif s == ".":
        return "."
    else:
        return "char"
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

# %% [markdown] tags=[]
# ## String manipulator 1: Shorten string

# %%
import random
random.seed('compgen')


# %%
def shorten(l:list) -> list:
    l_char_ix = [i for i,n in enumerate(l) if len(n) > 1 and type_code(n[0])=="char"]
    if len(l_char_ix) > 0:
        r = random.choice(l_char_ix)
        c = random.randint(1,len(l[r])-1)
        l[r] = l[r][0:c]
        if r+1 == len(l) or l[r+1] != ".":
            l.insert(r+1,".")            
    return l


# %%
data_shorten = {"".join(shorten(decompose(n))) for n in data}

# %% tags=[] jupyter={"outputs_hidden": true}
data_shorten


# %% [markdown]
# ## String manipulator 2: Drop characters

# %%
def drop(l:list) -> list:
    l_char_ix = [i for i,n in enumerate(l) if len(n) > 1 and type_code(n[0])=="char"]
    if len(l_char_ix) > 0:
        r = random.choice(l_char_ix)
        c = random.randint(1,len(l[r])-1)
        l[r] = l[r][0:c]+l[r][c+1:]
    return l


# %% [markdown]
# ## String manipulator 3: Linotype typing errors

# %%
from collections import defaultdict

# %% tags=[]
key_matrix_linotype = np.array([
    ['e', 'r', 'u', 'b',  '@', 'fl', '.', ',', '-',   '1', '6', 'E', 'R', 'U', 'B',],
    ['n', 'd', 'm', 'f',  '@', 'en', 'ä', '?', ':',   '2', '7', 'N', 'D', 'M', 'F',],
    ['i', 'g', 'l', 's',  '@', 'fi', 'ö', '@', '‘',   '3', '8', 'I', 'G', 'L', 'S',],
    ['a', 'o', 'h', 'k',  'ch', '”', 'ü', '@', '@',   '4', '9', 'A', 'O', 'H', 'K',],
    ['t', 'v', 'w', 'p',  'ck', 'ß', '“', '(', ')',   '5', '0', 'T', 'V', 'W', 'P',],
    ['x', 'c', 'y', 'z',  'j', 'q', 'J', '!', ';',    '@', '_', 'X', 'C', 'Y', 'Z',],
])

# %% tags=[]
key_matrix_linotype_reduced = np.array([
    ['e', 'r', 'u', 'b',  '@', 'fl', '@', '@', '@',   '1', '6', 'E', 'R', 'U', 'B',],
    ['n', 'd', 'm', 'f',  '@', 'en', 'ä', '@', '@',   '2', '7', 'N', 'D', 'M', 'F',],
    ['i', 'g', 'l', 's',  '@', 'fi', 'ö', '@', '@',   '3', '8', 'I', 'G', 'L', 'S',],
    ['a', 'o', 'h', 'k',  'ch', '@', 'ü', '@', '@',   '4', '9', 'A', 'O', 'H', 'K',],
    ['t', 'v', 'w', 'p',  'ck', '@', '@', '@', '@',   '5', '0', 'T', 'V', 'W', 'P',],
    ['x', 'c', 'y', 'z',  'j', 'q', 'J', '@', '@',    '@', '@', 'X', 'C', 'Y', 'Z',],
])

# %% tags=[] jupyter={"outputs_hidden": true}
neighbours_by_key = defaultdict(set)
rows = len(key_matrix_linotype_reduced)
cols = len(key_matrix_linotype_reduced[0])
for i in range (rows):
    for j in range (cols):
        c = key_matrix_linotype_reduced[i][j]
        if i > 0:    neighbours_by_key[c] |= {key_matrix_linotype[i-1][j]}
        if j > 0:    neighbours_by_key[c] |= {key_matrix_linotype[i][j-1]}
        if j < cols-1: neighbours_by_key[c] |= {key_matrix_linotype[i][j+1]}
        if i < rows-1: neighbours_by_key[c] |= {key_matrix_linotype[i+1][j]}
        neighbours_by_key[c].difference_update({'@'})
        digits = {str(n) for n in range(10)}
        if c in digits:
            neighbours_by_key[c].intersection_update(digits)
        else:
            neighbours_by_key[c].difference_update(digits)
del(neighbours_by_key['@'])
neighbours_by_key.default_factory = None
neighbours_by_key


# %% tags=[]
def lino(l:list) -> list:
    l_char_ix = [i for i,n in enumerate(l) if len(n) > 1 and type_code(n[0])=="char"]
    if len(l_char_ix) > 0:
        r = random.choice(l_char_ix)
        c = random.randint(1,len(l[r])-1)
        f = random.choice(list(neighbours_by_key[l[r][c]])) ## choose a random neighboured key
        l[r] = l[r][0:c]+f+l[r][c+1:]
    return l


# %%
s = decompose("""Very nicely written. In addition, the example chosen was itself lovely to play with.""")
for i in range(3):
    s = lino(shorten(drop(s)))
"".join(s)


# %% [markdown]
# ### Currying

# %% tags=[]
def w(l:list,f) -> list:
    l_char_ix = [i for i,n in enumerate(l) if len(n) > 1 and type_code(n[0])=="char"]
    if len(l_char_ix) > 0:
        r = random.choice(l_char_ix)
        l[r] = f(l[r])
    return l


# %% tags=[]
def lino(s:str):
    c = random.randint(1,len(s)-1)
    f = random.choice(list(neighbours_by_key[s[c]])) ## choose a random neighboured key
    return s[0:c]+f+s[c+1:]


# %%
s = decompose("""Very nicely written. In addition, the example chosen was itself lovely to play with.""")
"".join(w(decompose(s), lino))

# %% [markdown] tags=[]
# ## String manipulator 4: Fractal reading confusion errors

# %%

# %% [markdown] tags=[]
# ## String manipulator 3: Phonetic distortion

# %% [markdown]
# ### Kölner Phonetik

# %%
from compgen2 import Phonetic

# %%
