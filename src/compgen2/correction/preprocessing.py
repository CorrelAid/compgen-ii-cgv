# -*- coding: utf-8 -*-
"""Preprocessing class for 'WW1 Verlustliste' (raw input data)"""

import pandas as pd

class Preprocessing:
    
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
        str_10 = r'(\W*?nicht.*?)(?=,|$)' # preceding non-word characters + word 'nicht' + following content, until comma (not included) or end of line
        str_11 = r'(\W*?korr.*?|\W*?Korr\..*?)(?=,|$)' # preceding non-word characters + word 'korr' + following content, until (not including) comma or end of line
        str_12 = r'(\W*?verm.*?)(?=,|$)'  # preceding non-word characters + word 'verm' + following content, until (not including) comma or end of line

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
    def replace_characters_gov(column: pd.Series): 
        """Function for replacing special characters: 
        1. replaced with ': ´`
        Add more if necessary
        """
        
        # replace with special character (')
        char_1 = '[´`]'
        rep_1 = '\''
        
        # do replacement 
        return column.replace(to_replace=char_1, value=rep_1, regex=True)
    
    @staticmethod      
    def substitute_partial_words(column: pd.Series): 
        """Function no 1. for substituting abbreviations: flexibly substitutes abbreviations that are part of a longer word 
        (e.g. Oberfr./Mittelfr. -> franken)
        """
        
        # load defined abbreviations 
        sub = pd.read_csv("../data/substitutions_vl_gov_partial_word.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8')
        
        # add regex (THIS IS FUNCTION-SPECIFIC)
        sub.abbreviation = "(?<=\w)" + sub.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
        sub.expansion = sub.expansion.str.lower()
        
        # save as dict 
        subst_dict = dict(zip(sub.abbreviation, sub.expansion))
        
        # do replacement 
        return column.replace(to_replace=subst_dict, regex=True)
    
    @staticmethod      
    def substitute_delete_words(column: pd.Series): 
        """Function no 2. for substituting abbreviations: removes unnecessary abbreviations and words that relates to types 
        (e.g. Kr., Kreis, Amtshauptmannschaft)
        """
        
        # load defined abbreviations 
        sub = pd.read_csv("../data/substitutions_vl_gov_to_delete.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#', encoding ='utf-8') 
        
        # add regex and remove empty space (THIS IS FUNCTION-SPECIFIC)
        sub.abbreviation = "((?<=\W)|^)" + sub.abbreviation.replace(to_replace='\.', value='\\.', regex=True).str.lower()
        sub.expansion = sub.expansion.replace(to_replace=' ', value='')
        
        # save as dict 
        subst_dict = dict(zip(sub.abbreviation, sub.expansion))
        
        # do replacement 
        return column.replace(to_replace=subst_dict, regex=True)
    
    @staticmethod      
    def substitute_full_words(column: pd.Series): 
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
