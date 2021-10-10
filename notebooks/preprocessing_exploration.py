# -*- coding: utf-8 -*-
# %%
import pandas as pd
import numpy as np
import re
from preprocessing import Preprocessing

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
char = '\Wnicht'
verlustliste[verlustliste.location.str.contains(char)]

# %%
# Sonderzeichen ´ ` und ' vereinheitlichen auf ' 
verlustliste = verlustliste.replace({'location' : { '\´' : '\'', '\`' : '\''}}, regex=True)

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

# es kommen immer noch einzelne ( ) [ ] vor, vor allem in Kombination mit { } d.h. Tippfehler -> entfernen
verlustliste = verlustliste.replace({'location' : { '\(' : '', '\)' : '', '\[' : '', '\]' : '',}}, regex=True)

# %%
# Komplette Enfernung unsinniger Einträge (aktuell nur 1 Fall)
verlustliste[verlustliste.location.str.contains("!")]

chars = ['!']
verlustliste = verlustliste[~verlustliste.location.apply(lambda loc: any(c in loc for c in chars))]

# %%
# Sonderzeichen {} kennzeichnet Korrekturen aus moderner Zeit  
# 1) Fälle: A{achen}, A{.}chen -> {} entfernen
verlustliste = verlustliste.replace({'location' : { '\{' : '', '\}' : ''}}, regex=True)

# 2) Fall Achen {korr.: Aachen} -> korr.: (und ähnliche Varianten) in , umwandeln
verlustliste = verlustliste.replace({'location' : { 'korr.:' : ',', 'korr:' : ',', 'Korr.:' : ',', 'Korr:' : ',', 'korrekt:' : ',', 'verm.:' : ','}}, regex=True)

# %%
# Sonderzeichen / in Verbindung mit Abkürzungen (wie .) und Regionen (wie ,) 
# Sonderzeichen ; als Tippfehler für Komma 
# -> beide durch , ersetzen
verlustliste = verlustliste.replace({'location' : { '\/' : ',',  '\;' : ','}}, regex=True)

# %% [markdown]
# ### Test: Methoden aus Preprocessing

# %%
vl = verlustliste.copy()

# %%
vl = Preprocessing.prep_clean_brackets(vl)
vl

# %%
vl = Preprocessing.prep_clean_korrigiert(vl)
vl

# %%
# INFO: Zeige Einträge mit Sonderzeichen an 
#char = r'\(.*?\)'
#char = r'\('
#char = r'\Wnicht.*?'
char = r'(?i)korr'
#char = r'(?i)\Wverm.*?\.'  
vl[vl.location.str.contains(char)]

# %%
vl = Preprocessing.prep_clean_characters(vl)
vl

# %%
# INFO: Zeige Einträge mit Sonderzeichen an 
char = "\'"
vl[vl.location.str.contains(char)]

# %%
vl = Preprocessing.prep_vl_abbreviations(vl)

# %%
# Check: Prozentzahl an weiterhin bestehenden Abkürzungen
vl.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / vl.shape[0]

# %%
# Check: Häufigste weiterhin bestehende Abkürzungen
vl.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %%
# INFO: Zeige Einträge mit Sonderzeichen an 
char = "\."
char = "Oberf\."
vl[vl.location.str.contains(char)]

# %% [markdown]
# ## Abkürzungen erweitern

# %%
# INFO: Sonderzeichen . kennzeichnet Abkürzungen 

# %%
# Lade definierte Abkürzungserweiterungen
substitutions = pd.read_csv("../data/substitutions_PM.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#')

# %%
substitutions.info()

# %%
substitutions

# %%
# INFO: Abkürzungen ohne Bedeutung werden im Folgenden entfernt
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
# with_abbreviations = verlustliste[verlustliste.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()
# with_abbreviations

# %%
# INFO: Test Methode mit replace(regex=False)
# expanded = with_abbreviations.location.replace(replace_dict, regex=False)
# expanded

# Problem: Matched keine Substrings -> nicht geeignet

# %%
# INFO: Test Methode mit replace(regex=True)
# expanded_re = with_abbreviations.location.replace(replace_dict, regex=True)
# expanded_re

# Problem: Falsche Matches, da . in Dict als regex interpretiert wird -> nicht geeignet

# %%
# INFO: Test Methode mit str.replace, benötigt loop  
# for old, new in replace_dict.items():
#    with_abbreviations['location'] = with_abbreviations['location'].str.replace(old, new, regex=False)
# with_abbreviations

# Das funktioniert! 

# %%
# Ersetze Abkürzungen in Verlustliste
for old, new in replace_dict.items():
    verlustliste['location'] = verlustliste['location'].str.replace(old, new, regex=False)
verlustliste

# %%
# Check: Prozentzahl an weiterhin bestehenden Abkürzungen
verlustliste.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / verlustliste.shape[0]

# %%
# Check: Häufigste weiterhin bestehende Abkürzungen
verlustliste.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

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
