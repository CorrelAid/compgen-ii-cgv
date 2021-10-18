# -*- coding: utf-8 -*-
# %%
"""Preprocessing class for clearning special characters, brackets and abbreviations"""

# %%
import pandas as pd
import re


# %%
class Preprocessing:
    
    def prep_clean_brackets(data):
        """Function for removing historical corrections
        1. brackets including their content 
        2. the word 'nicht' plus the following content
        """
        
        # define cases 
        str_01 =  r'\(.*?\)' # brackets variants incl. content
        str_02 =  r'\(.*?\]'
        str_03 =  r'\[.*?\)'
        str_04 =  r'\[.*?\]'
        str_05 =  r'\(.*?\}'
        str_06 =  r'\{.*?\)'
        str_07 =  r'\[.*?\}'
        str_08 =  r'\{.*?\]'
        str_09 =  r'\Wnicht.*?' # additionally word ' nicht' and everything that comes after

        rep = ''
    
        # replace with remove 
        data['location'] = data['location'].replace(
            to_replace=[str_01, str_02, str_03, str_04, str_05, str_06, str_07, str_08, str_09], value=rep, regex=True)
        
        return (data)

    def prep_clean_korrigiert(data): 
        """Function for integrating modern-day corrections by replacing it with a comma
        1. word 'korrigiert' and its variants
        2. word 'vermutlich' and its variants
        """
        
        # define cases
        str_01 = r'(?i)\Wkorr.*?:' # word 'korrigiert' and it's variants; (?i) means ignore capitalization
        str_02 = r'(?i)\Wkorr.*?\.'
        str_03 = r'(?i)\Wkorr\W'
        str_04 = r'(?i)\Wverm.*?:' # word 'vermutlich' and it's variants
        str_05 = r'(?i)\Wverm.*?\.'  
        str_06 = r'(?i)\Wvermutlich\W'
        
        rep = ','

        # replace with comma 
        data['location'] = data['location'].replace(to_replace=[str_01, str_02, str_03, str_04, str_05, str_06], value=rep, regex=True)
        
        return (data)
             
    def prep_clean_characters(data): 
        """Function for removing special characters: 
        1. simply removed: ?^_"#*\:{}()[]!
        2. replaced with comma: /;
        3. replaced with ': ´`
        """
        
        # replace with remove 
        char_1 = '[?^_"#*\:{}()[\]!]'
        rep_1 = ''
        
        # replace with special character (comma)
        char_2 = '[/;]'
        rep_2 = ','
        
        # replace with special character (')
        char_3 = '[´`]'
        rep_3 = '\''
        
        # do replacement 
        data['location'] = data['location'].replace(to_replace=char_1, value=rep_1, regex=True).replace(
            to_replace=char_2, value=rep_2, regex=True).replace(
            to_replace=char_3, value=rep_3, regex=True)
        
        return (data)
        
    def prep_vl_abbreviations(data): 
        """Function for substituting abbreviations with predefined content"""
        
        # load defined abbreviations 
        substitutions = pd.read_csv("../data/substitutions_101021.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#')

        # save as dict 
        subst_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))
        
        # do replacement 
        for old, new in subst_dict.items():
            data['location'] = data['location'].str.replace(old, new, regex=False)

        return (data)

