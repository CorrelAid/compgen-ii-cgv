# -*- coding: utf-8 -*-
# %%
import pandas as pd
import numpy as np
import re
from compgen2 import GOV, Matcher, const, Preprocessing_VL, Preprocessing_GOV

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
vl

# %%
vl = Preprocessing_VL.replace_corrections_vl(vl)
vl

# %%
vl = Preprocessing_VL.replace_characters_vl(vl)
vl

# %%
vl

# %%
# INFO: Zeige Einträge an 
char = r'\Wnicht.*?'

vl[vl.location.str.contains(char)]

# %% [markdown]
# ## Abkürzungen erweitern

# %%
# INFO: Sonderzeichen . kennzeichnet Abkürzungen 

# %%
# Lade definierte Abkürzungserweiterungen
sub_partial = pd.read_csv("../data/substitutions_vl_gov_partial_word.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')

# %% [markdown]
# #### Prepare 'partial'

# %%
# preprocess: regex-compatible and lower case
sub_partial.abbreviation = "(?<=\w)" + sub_partial.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
#sub_partial.abbreviation

# %%
# abbreviations lower case
sub_partial.expansion = sub_partial.expansion.str.lower()
#sub_partial.expansion

# %%
# Substitutions in dict Format
replace_dict_1 = dict(zip(sub_partial.abbreviation, sub_partial.expansion))
#replace_dict_1

# %% [markdown]
# #### Prepare 'delete'

# %%
sub_delete = pd.read_csv("../data/substitutions_vl_gov_to_delete.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')

# %%
# preprocess: regex-compatible and lower case
sub_delete.abbreviation = "((?<=\W)|^)" + sub_delete.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
#sub_delete.abbreviation

# %%
# abbreviations lower case
sub_delete.expansion = sub_delete.expansion.replace(to_replace=' ', value='')

# %%
# Substitutions in dict Format
replace_dict_2 = dict(zip(sub_delete.abbreviation, sub_delete.expansion))
#replace_dict_2

# %% [markdown]
# #### Prepare 'full'

# %%
sub_full = pd.read_csv("../data/substitutions_vl_gov_full_word.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')

# %%
# preprocess: regex-compatible and lower case
sub_full.abbreviation = "((?<=\W)|^)" + sub_full.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
#sub_full.abbreviation

# %%
# abbreviations lower case
sub_full.expansion = sub_full.expansion.str.lower()
#sub_full.expansion

# %%
# Substitutions in dict Format
replace_dict_3 = dict(zip(sub_full.abbreviation, sub_full.expansion))
#replace_dict_3

# %% [markdown]
# #### Do all replacements

# %%
# TEST data set
with_abbreviations = vl[vl.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()
with_abbreviations["location"] = with_abbreviations["location"].str.lower()
with_abbreviations

# %%
testset = with_abbreviations.sample(n=50).drop('loc_parts_count', axis=1)
#testset

# %%
# INFO: Test Methode mit replace(regex=True)
testset['result_sub_partial'] = testset.location.replace(replace_dict_1, regex=True)
#testset

# Funktioniert! 

# %%
# INFO: Test Methode mit replace(regex=True)
testset['result_sub_delete'] = testset.result_sub_partial.replace(replace_dict_2, regex=True)
#testset

# Funktioniert! 

# %%
# INFO: Test Methode mit replace(regex=True)
testset['result_sub_full']= testset.result_sub_delete.replace(replace_dict_3, regex=True)
#testset

# Funktioniert! 

# %%
# INFO: Test Methode mit replace(regex=True)
testset['result_replace_i']= testset.result_sub_full.replace(to_replace=" i\.", value=",", regex=True)
#testset

# Funktioniert! 

# %% [markdown]
# #### Statistics

# %%
# with_abbreviations.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / with_abbreviations.shape[0]

# %%
# with_abbreviations.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %%
# Check: Prozentzahl an weiterhin bestehenden Abkürzungen
# vl.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / vl.shape[0]

# %%
# Check: Häufigste weiterhin bestehende Abkürzungen
# vl.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %% [markdown]
# ### Test: Methode aus Preprocessing

# %%
with_abbreviations = vl[vl.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()
with_abbreviations["location"] = with_abbreviations["location"]

# %%
testset = with_abbreviations.sample(n=50).drop('loc_parts_count', axis=1)

# %%
testset_2 = testset.copy()
#testset_2

# %%
testset_2['location'] = Preprocessing_VL.substitute_partial_words_vl(testset_2['location'])
#testset_2

# %%
testset_2['location'] = Preprocessing_VL.substitute_delete_words_vl(testset_2['location'])
#testset_2

# %%
testset_2['location'] = Preprocessing_VL.substitute_full_words_vl(testset_2['location'])
#testset_2

# %%
def substitute_full_words_vl(column: pd.Series): 
    """Function no 3. for substituting abbreviations: substitutes specific abbreviations"""
        
    # load defined abbreviations 
    sub = pd.read_csv("../data/substitutions_vl_gov_full_word.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')
        
    # add regex (THIS IS FUNCTION-SPECIFIC)
    sub.abbreviation = "((?<=\W)|^)" + sub.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
    sub.expansion = sub.expansion.str.lower()
        
    # save as dict 
    subst_dict = dict(zip(sub.abbreviation, sub.expansion))
        
    # do replacement 
    return column.replace(to_replace=subst_dict, regex=True)


# %%
testset_2['location'] = Preprocessing_VL.substitute_full_words_vl(testset_2['location'])

# %% [markdown]
# # GOV 

# %% [markdown]
# ### Abkürzungen erweitern

# %%
data_root = "../data"
gov = GOV(data_root)

# %%
gov.load_data()

# %%
gov.build_indices()

# %%
kreise = gov.get_names_by_ids(gov.get_ids_by_types(const.T_KREISUNDHOEHER))

# %%
kreise = list(kreise)
kreise = pd.DataFrame(data=kreise, columns=['name'])

# %%
kreise.info()

# %%
kreise.sample(n=20)

# %%
char = "(?i)königsberg"
kreise[kreise.name.str.contains(char)]

# %%
char = "(?i)j\. L\."
vl[vl.location.str.contains(char)]

# %%
