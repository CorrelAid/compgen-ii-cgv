# -*- coding: utf-8 -*-
"""Preprocessing class for Geschichtliches Ortsverzeichnis (GOV)"""

import pandas as pd

class Preprocessing_GOV:
    
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
    def replace_abbreviations_gov(column: pd.Series): 
        """Function for substituting abbreviations with predefined content"""
        
        # load defined abbreviations 
        substitutions = pd.read_csv("../data/substitutions_vl_gov.csv", sep = ";", header = None, names = ["abbreviation", "expansion"], comment='#')

        # save as dict 
        subst_dict = dict(zip(substitutions.abbreviation, substitutions.expansion))
        
        # do replacement 
        return column.replace(to_replace=subst_dict, regex=False)

