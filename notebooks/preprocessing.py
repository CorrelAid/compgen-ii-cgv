# -*- coding: utf-8 -*-
# %%
import pandas as pd
import numpy as np
import re

# %% [markdown]
# # Preprocessing

# %% [markdown]
# ## Verlustliste

# %%
# Lade verlustliste
verlustliste = pd.read_parquet("../data/deutsche-verlustlisten-1wk.parquet")

# %%
verlustliste.info()

# %%
verlustliste

# %% [markdown]
# ## Sonderzeichen ersetzen

# %%
# INFO: Verteilung der Sonderherzeichen anzeigen
import string
string.ascii_letters, string.punctuation

analysis_special_chars = {}
for char in string.punctuation + '´' + string.digits:
    df_ = verlustliste[verlustliste.location.str.contains(char, regex=False)]
    occurence = len(df_)
    analysis_special_chars[char] = (occurence, occurence / len(verlustliste), df_.loc_count.sum() / verlustliste.loc_count.sum())
    
from operator import itemgetter
sorted(analysis_special_chars.items(), key=itemgetter(1), reverse=True)

# %%
# INFO: Zeige Einträge mit Sonderzeichen an 
char = "\["
verlustliste[verlustliste.location.str.contains(char)]

# %%
# Sonderzeichen ´ ` und ' vereinheitlichen auf ' 
verlustliste = verlustliste.replace({'location' : { '´' : ''', '`' : '''}}, regex=True)

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

# es kommen immer noch einzelne ( ) [ ] vor, vor allem in Kombination mit { } d.h. Tippfehler -> ersetzen mit { } ?

# %%
# Komplette Enfernung unsinniger Einträge (aktuell nur 1 Fall)
verlustliste[verlustliste.location.str.contains("!")]

chars = ['!']
verlustliste = verlustliste[~verlustliste.location.apply(lambda loc: any(c in loc for c in chars))]

# %%
# TBD: Sonderzeichen {} kennzeichnet Korrekturen aus moderner Zeit

# %%
# TBD: Sonderzeichen / kennzeichnet sowohl Abkürzungen (wie .) als auch Regionen (wie ,)

# %% [markdown]
# ## Abkürzungen erweitern

# %%
# INFO: Sonderzeichen . kennzeichnet Abkürzungen 

# %%
# Lade definierte Abkürzungserweiterungen die im Rahmen der Masterarbeit von Dennis Sen erstellt wurden
substitutions = pd.read_csv("../data/substitutions.csv", sep = "\t", header = None, 
                            names = ["abbreviation", "expansion"], comment='#')

# %%
substitutions.info()

# %%
substitutions

# %%
## Leerzeilen entfernen
substitutions.dropna(how = "any", inplace=True)
substitutions

# %%
# INFO: Abkürzungen ohne Bedeutung werden entfernt (warum B.-A. hier vorkommt, ist unklar)
substitutions[substitutions.expansion == " "]

# %%
# INFO: Diese Abkürzungen werden durch Komma ersetzt
substitutions[substitutions.expansion == ", "]

# %%
# Substitutions in dict Format
replace_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))
replace_dict

# %%
# INFO: Test Methode mit str.replace() 
with_abbreviations = verlustliste[verlustliste.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()
with_abbreviations

# %%
# INFO: Test Methode mit replace(regex=False)
expanded = with_abbreviations.location.replace(replace_dict, regex=False)
expanded

# Problem: Matched keine Substrings

# %%
# INFO: Test Methode mit replace(regex=True)
expanded_re = with_abbreviations.location.replace(replace_dict, regex=True)
expanded_re

# Problem: Falsche Matches, da . in Dict als regex interpretiert wird 

# %%
# INFO: Test Methode mit str.replace, benötigt loop  
for old, new in replace_dict.items():
    with_abbreviations['location'] = with_abbreviations['location'].str.replace(old, new, regex=False)
with_abbreviations

# Das funktioniert! 

# %%
# Ersetze Abkürzungen in Verlustliste
for old, new in replace_dict.items():
    verlustliste['location'] = verlustliste['location'].str.replace(old, new, regex=False)
verlustliste

# %%
# Check percentage
verlustliste.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / verlustliste.shape[0]

# %%
# Check plot
verlustliste.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[:30]

# %% [markdown]
# Anmerkung: substitutions.csv Liste scheint nicht ideal für unsere Zwecke. Zum einen fehlen einige eindeutig identifizierbare Fälle (Unterfr. = Unterfranken, Mecklbg. = Mecklenburg). Zum anderen sind Typenersetzungen drin (z.B. Amtshauptmannschaft, Kreise) die wir vermutlich nicht brauchen, zumindest nicht als normale Matching-Spalte. Außerdem finden sich am Ende des Dokuments auch Wortkorrekturen, die wir eher über die Levenstein Distanz abdecken.  

# %%
# TBD: Restliche Sonderzeichen . entfernen

# %% [markdown]
# ### Save as parquet

# %%
verlustliste.to_parquet("../data/deutsche-verlustlisten-1wk_preprocessed.parquet")

# %% [markdown]
# ## GOV

# %%
gov = pd.read_parquet("../data/gov_orte_v01.parquet")

# %%
gov.info()

# %%
gov

# %%
# ´ ` und ' vereinheitlichen auf ' 
gov = gov.replace({'location' : { '´' : '\'', '`' : '\''}}, regex=True)

# %%
# Einträgt mit ? ! & + _ * > { } komplett entfernen
chars = ['?', '!', '&', '+', '_', '*', '>', '{', '}', ':']

gov = gov[~gov.location.apply(lambda loc: any(c in loc for c in chars))]
gov

# %%
# TBD: Abkürzungen mit . erweitern?

# %%
# TBD: Übersetzungen mit = getrennt aufsplitten?

# %% [markdown]
# ### Save as parquet

# %%
gov.to_parquet("../data/gov_orte_v01_preprocessed.parquet")

# %%
