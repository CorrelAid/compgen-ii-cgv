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

# %% [markdown] tags=[]
# # Synthetical data #14
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/14

# %% [markdown]
# Die 4 Übertragungs-Stationen der Verluste und ihre möglichen Veränderungen und Fehlerquellen
# 1. Kriegs-Front 
#     - Phonetische Fehler
#     - Geographische Fehler (z.B. "Aachen, Sachsen")
#     - Abkürzung von Wörtern
#     - **Frage**: Gab es so etwas wie ein Wehrregister aller gemeldeter Soldaten? Wie hat man bei einem Tod das Geburtstdatum des Soldaten erfahren?
# 2. Berlin, Kriegsministerium, Zentral-Nachweise-Büro
#     - Lesefehler (generell)
#     - Tippfehler (Linotype)
#     - Abkürzung von Wörtern
#     - **Frage**: Hat das Zentral-Nachweise-Büro in Berlin auch Korrekturen vorgenommen? 
#         * Offentsichtliche Fehler: z.B. "Köönigsberg i. Pr."
#         * Abgleich mit einem möglichen Wehrregister
# 3. Scan
#     - (keine besonderen Fehler)
# 4. Compgen Digitalisierung
#     - Lesefehler (generell, Frakturschrift)
#     - Tippfehler ((deutsche) Tastatur)

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
        t_curr = type_code(c)
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
# - word-based
# - Repetitve application to a word: Possible but not desired

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
# - character based
# - Repetitive application to a letter: Not applicable

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
# - character based
# - Repetitive application to a letter: Does not make sense

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
# ## String manipulator 3.2: German keyboard typing errors

# %% [markdown]
# Not considered so far

# %% [markdown] tags=[]
# ## String manipulator 4: Fractal reading confusion errors
# - character-based
# - Repetitive application to a letter: Does not make sense
# - KeyError: Not for every letter there is an entry in falsecouples_by_letter

# %%
fractal_confusion_pairs = {
    ('A','U'),
    ('D','O'),
    ('W','M'),
    ('N','R'),
    ('R','K'),
    ('S','G'),
    ('C','E'),
    ('V','B'),
    ('I','J'),
    ('d','b'),
    ('f','s'),
    ('r','x'),
    ('t','k'),
    ('u','n'),
    ('n','y'),
    ('y','h'),
    ('ß','tz'),
    ('ch','ck'),
    ('ck','d'),
    ('k','f'),
    ('t','i'),
    ('p','v'),
    ('b','h'),
}

# %% tags=[] jupyter={"outputs_hidden": true}
falsecouples_by_letter = defaultdict(set)
for p in fractal_confusion_pairs:
    falsecouples_by_letter[p[0]] |= {p[1]}
    falsecouples_by_letter[p[1]] |= {p[0]}
falsecouples_by_letter.default_factory = None
falsecouples_by_letter


# %%
def fractal(s:str):
    c = random.randint(1,len(s)-1)
    f = random.choice(list(falsecouples_by_letter[s[c]])) ## choose a random similar letter
    return s[0:c]+f+s[c+1:]


# %% tags=[]
s = decompose("""Very nicely written. In addition, the example chosen was itself lovely to play with.""")
"".join(w(decompose(s), fractal))

# %% [markdown] tags=[]
# ## String manipulator 5: Phonetic distortion

# %% [markdown]
# - character/phonem based

# %% [markdown]
# ### Kölner Phonetik

# %%
from compgen2 import Phonetic

# %%

# %% [markdown]
# ## String manipulator 6: Mix up space, dash
# - character-based

# %%
import re

def mix_up(s:str):
    return "!"

def three_digit_parser(s:str):
    pattern = re.compile(r"(?<!in)([- ])(?:[A-Z])", re.I)
    s_new = ""
    for i in range(len(s)):
        part = s[i-1 : i+2]
        if len(s) == 1:
            part = f" {s[0]} "
        elif i == 0:
            part = f" {s[:2]}"
        elif i == len(s) - 1:
            part = f"{s[i - 1:]} "
        if pattern.match(part):
            s_new += mix_up(s[i])
        else:
            s_new += s[i]
    return s_new


# %%
three_digit_parser("Hallo-Hallo")


# %% [markdown] tags=[]
# ## Chaining

# %%
def curryPartial(f, *args):
    if not callable(f): return f
    if f.__code__.co_argcount > len(args):
        return lambda *a: curryPartial(f, *(args + a))
    return f(*args[:f.__code__.co_argcount or None])


# %% tags=[]
def w(l:list,*args) -> list:
    l_char_ix = [i for i,n in enumerate(l) if len(n) > 1 and type_code(n[0])=="char"]
    if len(l_char_ix) > 0:
        r = random.choice(l_char_ix)
        for f in args:
            l[r] = f(l[r])
    return l


# %% tags=[]
def lino(s:str):
    c = random.randint(1,len(s)-1)
    f = random.choice(list(neighbours_by_key[s[c]])) ## choose a random neighboured key
    return s[0:c]+f+s[c+1:]


# %% jupyter={"source_hidden": true} tags=[]
s = decompose("""Very nicely written. In addition, the example chosen was itself lovely to play with.""")
"".join(w(decompose(s), lino))

# %%
