# -*- coding: utf-8 -*-
"""Preprocessing class for 'WW1 Verlustliste' (raw input data)"""

import pandas as pd

class Preprocessing_VL:
    
    @staticmethod
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
    
    @staticmethod        
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
    
    @staticmethod      
    def replace_abbreviations_vl(column: pd.Series): 
        """Function for substituting abbreviations with predefined content"""
        
        # load defined abbreviations 
        substitutions = pd.read_csv("../data/substitutions_101021.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#')

        # save as dict 
        subst_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))
        
        # do replacement 
        return column.replace(to_replace=subst_dict, regex=False)
