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
    
    def characters_vl(data): # -> pd.DataFrame:
        """
        """
        rep_1 = '\'' # replace with special character
        rep_2 = '' # remove 
        rep_3 = ',' # replace with comma
        
        # TBD bugfix: re.sub und re.compile ausprobieren
        data = data.replace({'location' : { r'\(.*\)', rep_2, r'\[.*\]', rep_2 , r'\(.*\]', rep_2, r'\[.*\)', rep_2,
                                          r'\(.*\}', rep_2, r'\[.*\}', rep_2 , r'\{.*\]', rep_2, r'\{.*\)', rep_2 }}, 
                            regex=True)
        
        data = data.replace({'location' : { '\´' : rep_1, '\`' : rep_1,
                                           '\?' : rep_2, '\^' : rep_2, '\_' : rep_2, '\"' : rep_2, '\#' : rep_2, '\*' : rep_2, '\\\\' : rep_2 , 
                                           '\{' : rep_2, '\}' : rep_2, '\(' : rep_2, '\)' : rep_2, '\[' : rep_2, '\]' : rep_2,
                                           'korr.:' : rep_3, 'korr:' : rep_3, 'Korr.:' : rep_3, 'Korr:' : rep_3, 'korrekt:' : rep_3, 'verm.:' : rep_3, 
                                           '\/' : rep_3,  '\;' : rep_3 }},
                            regex=True)

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

