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

# %% [markdown] tags=[]
# # Kölner Phonetik #43
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/43

# %%
import pandas as pd
import numpy as np
from compgen2 import GOV, Matcher, const, Phonetic
from pathlib import Path
import sys

# %%
data_root = "../data"
gov = GOV(data_root)

# %% tags=[]
gov.load_data()

# %%
gov.build_indices()

# %% [markdown]
# ## Kölner Phonetik

# %%
ph = Phonetic()

# %%
from collections import defaultdict

# %%
phonetic_by_name = {}
names_by_phonetic = defaultdict(set)
for n in gov.ids_by_name.keys():
    code = ph.encode(n)
    phonetic_by_name[n] = code
    names_by_phonetic[code] |= {n}
names_by_phonetic.default_factory = None

# %%
len(gov.ids_by_name.keys()), len(set(phonetic_by_name.values()))

# %% [markdown]
# ## Beispiele: Stärken

# %% [markdown]
# Die Kölner Phonetik definiert 9 unterschiedliche Laute und vergibt ihnen Codes von 0 bis 8.

# %% [markdown]
# Sämtliche **Vokale** werden auf "0" abgebildet. Außerdem werden alle "0" im finalen Code gelöscht, bis auf einen potentiellen Vokal am Anfang. Wegen dieser besonderen Behandlung von Vokalen ist die Kölner-Phonetik bei Fehlern in Vokalen besonders invariant.

# %%
print(ph.encode("Düsseldorf"))
print(ph.encode("Dassoldurf"))
print(names_by_phonetic["285273"])

# %% [markdown]
# Die Kodierung der Kölner-Phonetik reduziert außerdem einen Laut, der mehrmals hintereinander vorkommt auf, auf einen.

# %% tags=[]
print(ph.encode("DDDDDüssssselllllddddorf"))

# %% [markdown]
# Ähnlichklingende **Konsonanten** haben den selben Laut-Code

# %%
print(ph.encode("Düßeldorv"))

# %% [markdown]
# ## Beispiele: Schwächen

# %% [markdown]
# Was die Kölner-Phonetik **nicht** kann, ist gravierende Fehler in den Laut-Codes zu ignorieren. Der Buchstabe "L" erzeugt einen anderen Laut-Code als "D". Somit hat "Lüsseldorf" in der Kölner-Phonetik einen anderen Code.

# %%
print(ph.encode("Lüsseldorf"))

# %% [markdown]
# Insbesondere das **Hinzufügen von Konsonanten** kann die Kölner Phonetik nicht ignorieren.

# %%
print(ph.encode("Trakischken"))
print(ph.encode("Trakirschken"))

# %% [markdown]
# Ebenso das Hinzufügen von ganzen Wörtern verändert den Code.

# %%
print(ph.encode("Gr. Trakischken, Goldap"))
