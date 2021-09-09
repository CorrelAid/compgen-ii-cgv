# #Complete GOV extract #10
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/10

## Imports
import pandas as pd
import numpy as np
from pathlib import Path
path_here = Path(__file__).resolve().parent

#2404429 = 1. Januar 1871, 2420342 = 28. Juli 1914, 2421909 = 11. November 1918
T_BEGIN = 24219092 
T_END = 24044292
T_MIN = -2147483648
T_MAX = 2147483647

# 190315=Deutches Reich, 191050=Schweiz, 306245=Österreich-Ungarn, 220100=Liechtenstein, 218129=Luxemburg
SUPERNODES = {190315, 191050, 306245, 220100, 218129}

TKREIS_DEUTSCHESREICH = {5, 32, 36, 37, 110, 99, 78, 2, 149, 211, 212, 95} # Kreisähnliche Gebilde
TKREIS_ANDERE = {270, 25, 207, 134} # Kreisähnlich Österreich-Ungarn, Schweiz
TVERWALTUNG_DEUTSCHESREICH = {1, 53, 95, 18, 85, 144, 150, 218, 97} # unterste Verwaltungseinheiten
TVERWALTUNG_ANDERE = {275, 136} # Unterste Verwaltungsseinheit Österreich-Ungarn, Schweiz
TWOHNPLAETZE = {51, 55, 120, 230, 54, 39, 69, 129, 40, 54} # unterste Wohnplätze

TUNDESIRED = {47, 107 , 3, 19, 10 , 151 , 202 , 228 , 6, 9, 11, 12, 13, 26, 27, 28, 29, 35,
                 41, 42, 43, 44, 49, 91, 92, 96, 124, 153, 155, 206, 210, 219, 243, 244, 245,
                  249, 250, 253, 260, 263, 15, 89, 119, 166, 74, 98, 104, 147, 187, 195, 196,
                   197, 198, 199, 200, 103, 172, 242}
# Undesired are thes groups of GOV types:
# - Kirche
# - geographische Typen 
# - Zivilverwaltung
# - Gericht
# - Sonstige
# Desired are therefore these two groups of GOV types:
# - (politische) Verwaltung
# - Wohnplatz

def filter_time(data:pd.DataFrame) -> pd.DataFrame:
    data = data.replace({'time_begin':{np.NaN: T_MIN}, 'time_end':{np.NaN: T_MAX}},).astype({'time_begin':np.int64, 'time_end':np.int64,})
    data = data.query("time_begin < @T_BEGIN and time_end > @T_END") #TODO: Introduce correct time constraints for julian date???
    return data


def read_gov_item() -> pd.DataFrame:
    gov_item = pd.read_csv(path_here / "../data/gov_a_govitem.csv", 
                        sep="\t",
                        dtype={'id':np.int32, 'textual_id':object, 'deleted':np.int32},
                        )
    return gov_item

def read_names() -> pd.DataFrame:
    names = pd.read_csv(path_here / "../data/gov_a_propertynames.csv", 
                        sep="\t", 
                        dtype={'id':np.int32, 'content':object, 'language':object, 'time_begin':object, 'time_end':object},
                    )
    return names

def read_types() -> pd.DataFrame:
    types = pd.read_csv(path_here / "../data/gov_a_propertytypes.csv", 
                        sep="\t", 
                        dtype={'id':np.int32, 'content':np.int32, 'time_begin':object, 'time_end':object},
                    )
    return types

def read_relations() -> pd.DataFrame:
    relations = pd.read_csv(path_here / "../data/gov_a_relation.csv", 
                        sep="\t", 
                        dtype={'child':np.int32, 'parent':np.int32, 'time_begin':object, 'time_end':object},
                    )
    relations = filter_time(relations)
    return relations

def read_type_names() -> pd.DataFrame:
    type_names = pd.read_csv(path_here / "../data/gov_t_typenames.csv", 
                        sep="\t", 
                        index_col=0, 
                    )
    return type_names

def filter_names(names:pd.DataFrame) -> pd.DataFrame:
    names = names.query("language == 'deu'")
    return names

def build_gov_dict() -> dict:
    gov = read_gov_item()
    gov = set(zip(gov.id, gov.textual_id,gov.deleted,))
    gov_dict = {i[0]: (i[1],i[2],) for i in gov}
    return gov_dict

def build_name_dict() -> dict:
    names = filter_names(read_names())
    names = set(zip(names.id, names.content,))
    name_dict = dict()
    for n in names:
        name_dict[n[0]] = {n[1]}.union(name_dict.setdefault(n[0], set()))
    return name_dict  

def build_type_dict() -> dict:
    types = read_types()
    types = set(zip(types.id, types.content,))
    type_dict = dict()
    for t in types:
        type_dict[t[0]] = {t[1]}.union(type_dict.setdefault(t[0], set()))
    return type_dict

def filter_relations(relations_unfiltered:pd.DataFrame) -> set:
    """"
    Reduce the relations based on the SUPERNODES defined.
    Transform the relations to tuples
    """
    relations_unfiltered = set(zip(
                                relations_unfiltered.parent, 
                                relations_unfiltered.child, 
                                relations_unfiltered.time_begin,
                                relations_unfiltered.time_end,
                                ))
    relations_filtered = set()
    
    leaves_current = SUPERNODES
    new_leaves_found = True

    gov_dict = build_gov_dict()

    while new_leaves_found:
        leaves_next = set()
        for r in relations_unfiltered:
            if r[0] in leaves_current and gov_dict[r[1]][1] == 0:
                relations_filtered.add(r)
                leaves_next.add(r[1])
        relations_unfiltered.difference_update(relations_filtered)
        if len(leaves_next) == 0: new_leaves_found = False
        print(f"old: {len(relations_unfiltered)}, new: {len(relations_filtered)}, sample-child: {tuple(leaves_next)[:1]}")
        leaves_current = leaves_next
    return relations_filtered
    
def build_paths() -> set:
    relations = filter_relations(read_relations())
    leave_dict_curr =  {k: {((k,),T_MIN,T_MAX)} for k in SUPERNODES}
    paths = set()
    new_leaves_found = True
    while new_leaves_found:
        leave_dict_next = dict()
        leaves_updated = set()
        for r in relations:
            if r[0] in leave_dict_curr:
                for path in leave_dict_curr[r[0]]:
                    tmin = min(r[2], path[1]) 
                    tmax = max(r[3], path[2])
                    if tmin <= tmax: #TODO: Introduce correct time constraints???
                        leaves_updated.add(r[0])
                        path_updated = ((*path[0],r[1]), tmin, tmax)
                        leave_dict_next[r[1]] = {path_updated}.union(leave_dict_next.setdefault(r[1], set()))
        for l in leaves_updated:
            del leave_dict_curr[l]
        paths.update(*leave_dict_curr.values())
        if len(leaves_updated)==0: new_leaves_found = False
        print(f"Final paths: {len(paths)}, Updated paths: {len(set().union(*leave_dict_next.values()))}")
        leave_dict_curr = leave_dict_next
    paths = {p[0] for p in paths} # take path only without time_begin and time_end
    return paths

def decode_paths_id(paths:set) -> set:
    gov_dict = build_gov_dict()
    paths_decoded = {tuple(gov_dict[o][0] for o in p) for p in paths}
    return paths_decoded

def decode_paths_name(paths:set) -> set:
    name_dict = build_name_dict()
    paths_decoded = {tuple(name_dict[o].pop() for o in p) for p in paths}
    return paths_decoded

def filter_paths(paths:set) -> set:
    type_dict = build_type_dict()
    paths_filtered = {p for p in paths if not any([type_dict[n] & TUNDESIRED for n in p])}
    return paths_filtered

def extract_all_types_from_paths(paths:set) -> set:
    type_dict = build_type_dict()
    types_relevant = set().union(*[type_dict[n] for p in paths for n in p])
    return types_relevant


if __name__ == "__main__":
    types_relevant = extract_all_types_from_paths(filter_paths(build_paths()))
    print(types_relevant)











