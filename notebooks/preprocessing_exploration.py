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


# %%
def replace_corrections_vl(column: pd.Series):
    """Function for removing historical corrections '()[]' and modern-day corrections '{}' and variants
    1. brackets including their content 
    2. the word 'nicht' plus related content
    3. the word 'korrigiert' and its variants plus related content
    4. the word 'vermutlich' and its variants plus related content
    """
        
    # define cases 
    str_01 = r'\(.*?\)' # bracket variants incl. content
    str_02 = r'\[.*?\]'
    str_03 = r'\{.*?\}'
    str_04 = r'\(.*?\]'
    str_05 = r'\[.*?\)'
    str_06 = r'\(.*?\}'
    str_07 = r'\{.*?\)'
    str_08 = r'\[.*?\}'
    str_09 = r'\{.*?\]'
    str_10 = r'(\Wnicht.*?)(?=,|$)' # word 'nicht' and following content, until (not including) comma or end of line
    str_11 = r'(\Wkorr.*?|\WKorr\..*?)(?=,|$)' # word 'korr' and following content, until (not including) comma or end of line
    str_12 = r'(\Wverm.*?)(?=,|$)'

    rep = ''
    
    # replace with remove 
    return column.replace(
        to_replace=[str_01, str_02, str_03, str_04, str_05, str_06, str_07, str_08, str_09, str_10, str_11, str_12], value=rep, regex=True)
    
vl = replace_corrections_vl(vl)

# %%
vl


# %%
def replace_characters_vl(column: pd.Series): 
    """Function for removing special characters: 
    1. simply removed: ?^_"#*\:{}()[]!
    2. replaced with ': ´`
    """
        
    # replace with remove 
    char_1 = '[?^_"#*\:{}()[\]!]'
    rep_1 = ''
        
    # replace with special character (')
    char_2 = '[´`]'
    rep_2 = '\''
        
    # do replacement 
    return column.replace(to_replace=[char_1, char_2], value=[rep_1, rep_2], regex=True)

vl = replace_characters_vl(vl)

# %%
vl

# %%
# INFO: Zeige Einträge an 
char = "Pr.-"

vl[vl.location.str.contains(char)]


# %%
#vl = Preprocessing.prep_vl_abbreviations(vl)

# %%
# Check: Prozentzahl an weiterhin bestehenden Abkürzungen
#vl.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / vl.shape[0]

# %%
# Check: Häufigste weiterhin bestehende Abkürzungen
#vl.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %%
# INFO: Zeige Einträge mit Sonderzeichen an 
char = "\."
#vl[vl.location.str.contains(char)]
verlustliste[verlustliste.location.str.contains(char)]

# %% [markdown]
# ## Abkürzungen erweitern

# %%
# INFO: Sonderzeichen . kennzeichnet Abkürzungen 

# %%
# Lade definierte Abkürzungserweiterungen
sub1 = pd.read_csv("../data/substitutions_vl_gov_utf8.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')

# %%
# preprocess: regex-compatible and lower case
sub1.abbreviation = "((?<=\W)|^)" + sub1.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
sub1.abbreviation

# %%
# abbreviations lower case
sub1.expansion = sub1.expansion.str.lower()
sub1.expansion

# %%
# INFO: Diese Abkürzungen werden im Folgenden entfernt
sub1[sub1.expansion == " "]

# %%
# Lade definierte Abkürzungserweiterungen
sub2 = pd.read_csv("../data/substitutions_vl_gov_lc_utf8.csv", sep = ";", header = None, 
                            names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')

# %%
# preprocess: regex-compatible and lower case
sub2.abbreviation = "(?<=\w)" + sub2.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
sub2.abbreviation

# %%
# abbreviations lower case
sub2.expansion = sub2.expansion.str.lower()
sub2.expansion

# %%
substitutions = pd.concat([sub1, sub2])
substitutions

# %%
# Substitutions in dict Format
replace_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))
replace_dict

# %%
# TEST data set
with_abbreviations = vl[vl.location.str.contains("[A-Za-zäöüßÄÖÜẞ]+\.")].copy()
with_abbreviations["location"] = with_abbreviations["location"].str.lower()
with_abbreviations

# %%
testset = with_abbreviations.sample(n=20)
testset

# %%
# INFO: Test Methode mit replace(regex=True)
testset.location = testset.location.replace(replace_dict, regex=True)
testset

# Funktioniert! 

# %%
with_abbreviations.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / with_abbreviations.shape[0]

# %%
with_abbreviations.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %%
# INFO: Zeige Einträge an 
char = "kl\."

with_abbreviations[with_abbreviations.location.str.contains(char)]

# %%
# Ersetze Abkürzungen in Verlustliste
# vl.location = vl.location.replace(replace_dict, regex=True)
# vl

# %%
# Check: Prozentzahl an weiterhin bestehenden Abkürzungen
# vl.location.str.count("[A-Za-zäöüßÄÖÜẞ]+\.").sum() / vl.shape[0]

# %%
# Check: Häufigste weiterhin bestehende Abkürzungen
# vl.location.str.extract("(?P<Abkürzung>[A-Za-zäöüßÄÖÜẞ]+\.)").dropna().value_counts(normalize = True)[0:50]

# %% [markdown]
# # GOV 

# %% [markdown]
# ## Abkürzungen überprüfen

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
char = "(?i)i\."
kreise[kreise.name.str.contains(char)]

# %%
char = "(?i)i\."
verlustliste[verlustliste.location.str.contains(char)].sample(n=20)

# %%
