# -*- coding: utf-8 -*-
# %%
"""Preprocessing class

Add info here: 

"""

# %%
import pandas as pd
import re


# %%
class Preprocessing:
    """
    """
    
    def prep_vl_multi(data): # -> pd.DataFrame:
        """
        """
        
        # MULTIPLE CHARACTERS (strings)
        
        # replace with remove 
        str_01 =  r'\(.*?\)' # brackets incl. content
        str_02 =  r'\(.*?\]'
        str_03 =  r'\[.*?\)'
        str_04 =  r'\[.*?\]'
        str_05 =  r'\(.*?\}'
        str_06 =  r'\{.*?\)'
        str_07 =  r'\[.*?\}'
        str_08 =  r'\{.*?\]'
        str_09 =  r'\Wnicht.*?' # word ' nicht' and everything that comes after (tbd: only until next comma if there is a comma)
        str_10 = r'\Wverm.*?\W' # word ' vermutlich ' and it's variants 
        rep_1 = ''
        
        # replace with special character (comma)
        str_11 = r'(?i)korr.*?:' # word variants for 'korrekt' 
        str_12 = r'(?i)korr\.'
        str_13 = r'(?i)\Wkorr\W'
        rep_2 = ','

        data['location'] = data['location'].replace(
            to_replace=[str_01, str_02, str_03, str_04, str_05, str_06, str_07, str_08, str_09, str_10], value=rep_1, regex=True).replace(
            to_replace=[str_11, str_12, str_13], value=rep_2, regex=True)
        
        return (data)
             
    def prep_vl_single(data): # -> pd.DataFrame:
        """
        """

        # SINGLE CHARACTERS (run after MULTIPLE CHARACTERS)
        
        # replace with remove 
        char_1 = '[?^_"#*\:{}()[\]]'
        rep_1 = ''
        
        # replace with special character (comma)
        char_2 = '[/;]'
        rep_2 = ','
        
        # replace with special character (')
        char_3 = '[´`]'
        rep_3 = '\''
        
        
        data['location'] = data['location'].replace(to_replace=char_1, value=rep_1, regex=True).replace(
            to_replace=char_2, value=rep_2, regex=True).replace(
            to_replace=char_3, value=rep_3, regex=True)
        
        return (data)
        
    def abbreviations_vl(data):
        """
        """
        

        pass
    
#    def characters_gov(data):
#        """
#        """
#        pass
#        
#    def abbreviations_gov(data):
#        """
#        """
#        pass

