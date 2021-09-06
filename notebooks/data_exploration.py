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

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %%
verlustliste.head(10)

# %%
verlustliste.tail(10)

# %%
verlustliste.sample(10)

# %%
f"{len(verlustliste):,d}"

# %% [markdown]
# Der Datensatz enthält insgesamt 1,2 Millionen Orte bzw. einmalige Nennungen

# %%
f"{verlustliste.loc_count.sum():,d}"  # Gesamttodesfälle

# %% [markdown]
# Der Datensatz enthält insgesamt 8,3 Millionen Nennungen bzw. Verluste/Opfer

# %% [markdown]
# ## Verteilungen

# %% [markdown]
# ### Analyse/Bedeutung der Namensbestandteile

# %%
verlustliste.loc_parts_count.value_counts()

# %%
verlustliste.loc_parts_count.value_counts() / len(verlustliste)

# %%
data = verlustliste.loc_parts_count.value_counts()
x = data.index
heights = data.values

plt.bar(x, heights, width=0.7, alpha=0.8, edgecolor="k")
plt.yscale("log")
#plt.xticks(range(1,6))
plt.xlabel("Bestandteile pro Namen")
plt.ylabel("Abs. Häufigkeit")
plt.title("Verteilung der Bestandteile pro Namen")

# %% [markdown]
# Angaben mit 2 Bestandteilen sind am häufigsten (knapp 1 Million), gefolgt von Angaben mit nur einem Namen und Angaben mit 3 Bestandteilen.

# %%
verlustliste.query("loc_parts_count in [1,2,3]").shape[0] / verlustliste.shape[0]

# %% [markdown]
# Wir sehen, dass die Einträge mit Namensbestandsteilen bis max. 3 bereits 99,99 % aller Einträge ausmachen. Das ist allerdings noch ohne Berücksichtigung der tatsächlich dort Gefallenen, also der Anzahl der Nennungen dieses Ortes.

# %%
verlustliste.query("loc_parts_count in [1,2,3]").loc_count.sum() / verlustliste.loc_count.sum()

# %% [markdown]
# Aber auch dann bleibt es bei 99,99 %, d.h. die Summe aller Nennungen für die Einträge mit Namensbestandteilen bis max. 3 entspricht 99,99 % der Gesamtnennungen

# %% [markdown]
# Welche Rolle spielen die Namen mit genau 3 Bestandteilen?

# %%
print(verlustliste.query("loc_parts_count in [1,2]").shape[0] / verlustliste.shape[0])
print(verlustliste.query("loc_parts_count in [1,2]").loc_count.sum() / verlustliste.loc_count.sum())

# %% [markdown]
# Selbst wenn wir uns nur auf die Namen mit 1 oder 2 Bestandteilen konzentrieren, können wir damit bereits 97 % der Einträge und 99,45 % der Gesamtnennungen abdecken.

# %% [markdown]
# ### Location count

# %%
# Häufigsten Nennungen insgesamt
verlustliste.sort_values("loc_count", ascending=False)

# %%
verlustliste.query("loc_count > 20000")

# %%
verlustliste.query("loc_count > 20000").loc_count.sum() / len(verlustliste)

# %%
# Verteilung der N häufigsten Nennungen
plt.figure(figsize=(20,6))

df_ = verlustliste.sort_values("loc_count", ascending=False)

N = 20
plt.bar(df_["location"][:N], df_["loc_count"][:N])

# %%
# Verteilung der N häufigsten Nennungen, gruppiert nach Namensbestandteilen
N = 20

fig, ax = plt.subplots(5,1, figsize=(15, 18))

for i, count in enumerate(verlustliste.loc_parts_count.unique()):
    
    data = verlustliste.query("loc_parts_count == @count").sort_values("loc_count", ascending=False)
    
    ax[i].bar(data["location"][:N].map(lambda x: x[:10]), data["loc_count"][:N])
    ax[i].set_title(f"loc_parts_count == {count}")


plt.tight_layout()
fig.suptitle(f"Die ersten {N} häufigsten Städte pro Anzahl Namensbestandteil")
    

# %% [markdown]
# Wir sehen, dass die Häufigkeiten stark mit der Anzahl der Namensbestandteile abgeben, je kleiner der Ort bzw. je schwerer zu spezifizieren, desto unbedeutender wird er für die Gesamtstatistik. Nennungen mit 4 oder 5 Bestandteilen kommen absolut gesehen nicht mehr als 2 mal pro Nennung vor. Wie viele gibt es davon?

# %%
verlustliste.query("loc_parts_count in [4,5]").shape[0]

# %% [markdown]
# Es gibt insgesamt nur 174 Nennungen mit mehr als 3 Bestandteilen

# %% [markdown]
# ## Regionen ( erstmal nur mit loc_parts_count == 2)

# %%
data = verlustliste.query("loc_parts_count == 2")
data

# %%
# Füge den zweiten Bestandteil als neue Spalte "rehion" hinzu
data = data.assign(region=data.location.str.split(",", expand=True)[1])

# %%
data

# %%
# Verteilung der Regionen
plt.figure(figsize=(20,6))

x = data.value_counts("region").index
heights = data.value_counts("region").values

N = 20
plt.bar(x[:N], heights[:N], alpha=0.8, edgecolor="k")

plt.xlabel("2. Bestandteil")
plt.ylabel("Abs. Häufigkeit")
plt.title(f"Verteilung der {N} häufigsten Regionen (für 2 Namensbestandteile)")

# %%
df_ = data.region.value_counts()

df_[df_ == 1]

# %%
df_[df_ == 1].shape[0] / df_.shape[0]

# %% [markdown]
# ## Sonderzeichen

# %%
import string

string.ascii_letters, string.punctuation

# %%
analysis_special_chars = {}
for char in string.punctuation + '´' + string.digits:
    df_ = verlustliste[verlustliste.location.str.contains(char, regex=False)]
    occurence = len(df_)
    analysis_special_chars[char] = (occurence, occurence / len(verlustliste), df_.loc_count.sum() / verlustliste.loc_count.sum())

# %%
from operator import itemgetter

sorted(analysis_special_chars.items(), key=itemgetter(1), reverse=True)

# %%
# Zahlen 
verlustliste[verlustliste.location.str.contains("2")]

# %%
# 75492 Einträge mit Bindestrich
verlustliste[verlustliste.location.str.contains("-")]

# %%
# 10 Einträge mit ^
verlustliste[verlustliste.location.str.contains("\^")]

# %%
verlustliste[verlustliste.location.str.contains("`")]

# %%
# 29 Einträge mit ´
verlustliste[verlustliste.location.str.contains("´")]

# %% [markdown]
# # Preprocessing VL

# %%
# Sonderzeichen ´ ` und ' vereinheitlichen auf ' 
verlustliste = verlustliste.replace({'location' : { '´' : '\'', '`' : '\''}}, regex=True)

# %%
# Sonderzeichen ? ^ _ " # * entfernen 
verlustliste = verlustliste.replace({'location' : { '\?' : '', '\^' : '', '\_' : '', '\"' : '', '\#' : '', '\*' : '', '\\\\' : ''  }}, regex=True)

# %%
# Sonderzeichen () und [] kennzeichnen Korrekturen aus historischer Zeit -> inklusive Inhalt entfernen
verlustliste['location'] = verlustliste['location'].str.replace(r"\(.*\)","")
verlustliste['location'] = verlustliste['location'].str.replace(r"\[.*\]","")

# weitere vorkommende Varianten
verlustliste['location'] = verlustliste['location'].str.replace(r"\(.*\]","")
verlustliste['location'] = verlustliste['location'].str.replace(r"\[.*\)","")
verlustliste['location'] = verlustliste['location'].str.replace(r"\(nicht.*","")
verlustliste['location'] = verlustliste['location'].str.replace(r"\[nicht.*","")

# es kommen immer noch einzelne ( ) [ ] vor, vor allem in Kombination mit { } (Tippfehler) -> ersetzen mit { } ?

# %%
# Aktuell nicht verwendet: Code um Einträge komplett zu entfernen
# chars = ['!']
# verlustliste = verlustliste[~verlustliste.location.apply(lambda loc: any(c in loc for c in chars))]

# %%
# TBD: Sonderzeichen {} kennzeichnet Korrekturen aus moderner Zeit

# %%
# TBD: Sonderzeichen . kennzeichnet Abkürzungen -> Flo Abkürzungen erweitern

# %%
# TBD: Sonderzeichen / kennzeichnet sowohl Abkürzungen (wie .) als auch Regionen (wie ,)

# %%
# Sonderzeichen , -> Split in einzelne Bestandteile 
verlustliste_mit_regionen = verlustliste.location.str.split(",", expand=True)
verlustliste_mit_regionen.columns = ["location", "1","2","3","4"]

# %%
verlustliste_mit_regionen

# %% [markdown]
# ## Save as parquet

# %%
verlustliste_mit_regionen.to_parquet("../data/deutsche-verlustlisten-1wk_preprocessed.parquet")

# %%
