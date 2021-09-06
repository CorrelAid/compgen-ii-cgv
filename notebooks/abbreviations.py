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
import re

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %%
verlustliste

# %% [markdown]
# # EDA: Abkürzungen in den Verlustlisten

# %% [markdown]
# ## Relative Häufigkeit von Abkürzungen in den Verlustlisten

# %%
verlustliste.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / verlustliste.shape[0]

# %% [markdown]
# In 33% aller Einträge befindet sich eine Abkürzung (d. h. mindestens ein Buchstabe und danach ein Punkt). Buchstaben, die nur im Deutschen vorkommen (`äöüß`), müssen bei Regex-Matching gesondert berücksichtigt werden.

# %%
verlustliste.location.str.count("[^A-Za-zäöüßÄÖÜẞ]\.").sum() / verlustliste.shape[0]

# %%
verlustliste[verlustliste.location.str.contains("[^A-Za-zäöüßÄÖÜẞ]+\.")]

# %%
verlustliste.location.str.count("{\.").sum() / verlustliste.shape[0]

# %% [markdown]
# In wenigen Fällen (0,4%) tritt ein Punkt ohne Buchstaben auf, das heißt es handelt sich nicht um eine Abkürzung. In den meisten dieser Fälle (0,35% von 0,4%) handelt es sich dabei um eine Korrektur der Digitalisierer. Diese wird durch eine geschweifte Klammer `{`  eingeleitet und ein Punkt kennzeichnet in diesem Fall einen nicht lesbaren Buchstabens (und dementsprechend mehrere Punkte mehrere nicht lesbare Buchstaben).

# %%
verlustliste[verlustliste.location.str.contains("[^A-Za-zäöüßÄÖÜẞ{]+\.")]

# %%
verlustliste[verlustliste.location.str.contains("\[\.")]

# %% [markdown]
# Sehr, sehr wenige Korrekturen wurden nach dem oben beschriebenen Schema bereits in der historischen Abschrift der Verlustlisten
# gemacht und durch `[` kenntlich gemacht.

# %%
verlustliste[verlustliste.location.str.contains("[{]\.")]

# %% [markdown]
# ## Verteilung der unterschiedlichen Abkürzungen

# %%
frequencies = verlustliste.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts()

# %%
frequencies.hist(bins = 100)

# %%
rel_frequencies = verlustliste.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)
rel_frequencies[:30].plot.bar()

# %%
rel_frequencies.cumsum()[:30]

# %% [markdown]
# Die allermeisten Abkürzungen kommen genau einmal vor. Die 30 häufigsten Abkürzungen machen 85% aller Abkürzungen aus.

# %% [markdown]
# # EDA und Bereinigung der Abkürzungsliste (aus MA-Arbeit)

# %%
substitutions = pd.read_csv("../data/substitutions.csv", sep = "\t", header = None, 
                            names = ["abbreviation", "expansion"], comment='#')

# %%
substitutions.info()

# %%
substitutions[15:25]

# %%
substitutions.dropna(how = "any")

# %% [markdown]
# Es gibt einige Leerzeilen (beide Spalten `NaN`) in der Abkürzungsliste. Diese ergeben sich dadurch, dass die Abkürzungen in mehrere Unterpunkte gegliedert ist, die die Art der Abkürzung angeben, z. B. *administration (departments), word end expansions*). Die Gliederungspunkte sind mit einer Leerzeile und danach einem `#`abgetrennt. Da die Art der Abkürzung für uns nicht relevant ist sind, sondern nur die Abkürzungen selbst, werden sie aus dem Datensatz entfernt. Dazu wurden oben in `pd.read_csv()` mit `comment='#'` auch schon die Kommentarzeilen entfernt.

# %%
substitutions[substitutions.expansion == " "]

# %% [markdown]
# Abkürzungen, die keine weitere inhaltliche Bedeutung haben (*wohn.* = wohnhaft, *v.* = von, d.?) werden herausgekürzt. Das *B.-A.* auch herausgekürzt wird, ist meine Erachtens ein Datenfehler. Denn die anderen Abkürzungen finden sich alle unter dem Gliederungspunkt *common other abbreviations*, während *B.-A.* als einzige Abkürzung unter dem Gliederungspunkt *administration (departments)* auftaucht.

# %%
substitutions[substitutions.expansion == ", "]

# %% [markdown]
# Es gibt Abkürzungen, denen ein Komma zugeodnet wird, da nach dieser Abkürzung wahrscheinlich die geographisch nächsthöhere geographische Gliederungsebene folgt. Möglicherweise macht es hier aber Sinn zwischen b. = bei und i. = in zu unterscheiden.

# %% [markdown]
# # Expansion der Abkürzungen der Verlustliste durch die Abkürzungsliste

# %%
replace_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))

# %%
my_series = pd.Series(['Russ.', 'Ruß.', 'Rus', 'bla Russ. bla Russ. bla', 'Rußland', 'Stockach', 'Kr', 'Kr.', 'blabla Kr. blabla''b.' ])

# %%
my_series.replace(replace_dict)

 # %%
 my_series.replace(replace_dict, regex = True)

# %%
my_series.replace({'St.': 'Sankt', 'Skt.': 'Sankt'})

# %%
{'St.': 'Sankt', 'Skt.': 'Sankt'}

# %%
replace_dict

# %%
with_abreviations = verlustliste[verlustliste.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")]

# %%
with_abreviations

# %%
expanded = with_abreviations.location.replace(replace_dict)

# %%
expanded

# %%
expanded_regex = with_abreviations.location.replace(replace_dict, regex = True)

# %%
expanded_regex

# %%

# %%
verlustliste["location"] = verlustliste.location.replace(replace_dict, regex = True)

# %%
verlustliste.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / verlustliste.shape[0]

# %% [markdown]
# Nach der Expansion der Abkürzungen durch die Abkürzungsliste enthalten nur noch 14%, stattt 33% aller Einträge Abkürzungen.

# %%
verlustliste.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[:30]

# %% [markdown]
# Es gibt trotzdem noch einige Abkürzungen, die relativ häufig vorkommen.

# %% [markdown]
# # Speichern als parquet

# %%
verlustliste.to_parquet("../data/deutsche-verlustlisten-1wk-expandierte-abk.parquet")

# %% [markdown]
# Da das expandieren der Abkürzungen ca. 15 Minuten dauert, speichere ich den Datensatz mit den ausgeschriebenen Abkürzungen ab.

# %% [markdown]
# # Laden als parquet

# %%
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk-expandierte-abk.parquet")

# %%
