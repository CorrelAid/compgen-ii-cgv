"""This module contains the Matcher class that provides the main logic to match names against the Gov database.

Examples:
```Python
m = Matcher(gov)
m.get_match_for_locations(["Aachen", "aarösund, flensburg"])
print(m.results)
```
"""
import logging
from collections import defaultdict
from itertools import product
from operator import itemgetter
from typing import Optional, Union

import pandas as pd
from tqdm import tqdm

import difflib

from .. import LocCorrection
from ..const import T_KREISUNDHOEHER, T_STADT
from . import Gov
from .. import Phonetic

logger = logging.getLogger(__name__)

class Matcher:
    """Main class to match names against the Gov database.
    
    Main steps of the matching algorithm:
        1. ...
        
    Attributes:
        gov (Gov): A fully initialized instance of the Gov class.
        results (dict): A dictionary containing the final results. 
            Provides information about the found parts and the possible matches for each query.
    """
    def __init__(self, gov: Gov) -> None:
        self.gov = gov
        self.results = {}

        if not self.gov.fully_initialized:
            logger.warning(
                "Passed instance of gov is not fully initialized. "
                "Make sure to run `load_data()` and `build_indices()`."
            )
        else:
            logger.info(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

        self.koelner_phonetic = Phonetic()
        self.names_by_phonetic = defaultdict(set)
        for name in gov.get_loc_names():
            self.names_by_phonetic[self.koelner_phonetic.encode(name)] |= {name}
        self.names_by_phonetic.default_factory = None

        self.anchor_method = []

        self.use_difflib = True
        self.levenshtein_max_cost = 3
        self.anchor_flag_kreis = False
        self.anchor_flag_phonetic = False

    def get_match_for_locations(self, locations: Union[list[str], pd.Series]) -> None:
        for location in tqdm(locations, desc="Processing locations"):
            self.find_parts_for_location(location)
            self.find_textual_id_for_location(location)


    def find_parts_for_location(self, location: str) -> None:
        """Find the Gov parts for each location name.

        If a part is not found in the Gov in its original form, we try to find better candidates.
            Candidates are found by using the Levenshtein distance.

        This method fills the 'parts' dictionary of self.result[location].
            For each part of location, there will be a new entry with
                - in_gov (bool): True, if part is part of Gov, False otherwise.
                - candidates (list): A list of possible candidates in Gov.

        Args:
            location (str): location names, e.g. "aachen, alsdorf".
        """
        self.results[location] = {"parts": {}}
        parts = Matcher.get_query_parts(location)
        for part in parts:
            in_gov = True if part in self.gov.ids_by_name else False
            self.results[location]["parts"][part] = {
                "in_gov": in_gov,
                "candidates": [part] if in_gov else [],
                }

        if all(part["in_gov"] for part in self.results[location]["parts"].values()):
            self.anchor_method.append("gov complete")
            return

        # first handle case that we did not find anything for any part
        # try to find at least one candidate for any part
        if not any(part["in_gov"] for part in self.results[location]["parts"].values()):
            matched_part, candidates = self.find_part_with_best_candidates(parts)

            if candidates:
                self.results[location]["parts"][matched_part]["candidates"].extend(candidates)
            else:
                self.anchor_method.append("No anchor at all")
        else:
            self.anchor_method.append("gov partial")

        # now check if there is still one part without a match
        # and use the already matched part to get relevant names
        if len(parts) > 1:
            parts = self.results[location]["parts"]
            relevant_names = set()
            for matched_part in [part for part, partdict in self.results[location]["parts"].items() if partdict["in_gov"] or partdict["candidates"]]:
                candidates = self.results[location]["parts"][matched_part]["candidates"]
                relevant_names.update(self.get_relevant_names_from_part_candidates(candidates))
            for unmatched_part in [part for part, partdict in self.results[location]["parts"].items() if not (partdict["in_gov"] or partdict["candidates"])]:
                candidates = self.get_matches(unmatched_part, relevant_names, self.levenshtein_max_cost)
                self.results[location]["parts"][unmatched_part]["candidates"].extend(candidates)
                relevant_names.update(self.get_relevant_names_from_part_candidates(candidates))


    def find_textual_id_for_location(self, location: str) -> None:
        """Find a textual id for given location name."""
        
        self.results[location]["possible_matches"] = []

        list_of_candidates = [
            part["candidates"] for part in self.results[location]["parts"].values() if part["candidates"]
        ]

        if list_of_candidates:
            for combination_of_names in product(*list_of_candidates):
                ids_for_combination = (self.gov.ids_by_name[name] for name in combination_of_names)
                for ids in product(*ids_for_combination):
                    if len(ids) > 1:
                        # TODO: what to do if items exist in Gov but not the relationship?
                        if not self.gov.all_reachable_nodes_by_id[ids[0]].issuperset(ids[1:]):
                            continue
                    
                    match = {}
                    for i, part in enumerate(combination_of_names):
                        gov_id = ids[i]
                        textual_id = self.gov.items_by_id[gov_id]
                        type_ids = list(self.gov.types_by_id[gov_id])
                        type_names = [self.gov.type_names_by_type[type_id] for type_id in type_ids]
                        match[part] = {
                            "gov_id": ids[i],
                            "textual_id": textual_id,
                            "type_ids": type_ids,
                            "type_names": type_names
                        }
                    
                    self.results[location]["possible_matches"].append(match)

    def find_part_with_best_candidates(self, parts: tuple[str]) -> tuple[str, list[str]]:
        if self.anchor_flag_kreis:
            for type_ids in [T_KREISUNDHOEHER, T_STADT]:
                for cost in range(1, 3 + 1):
                    for part in parts:
                        relevant_names = self.get_loc_names(type_ids)
                        candidates = self.get_matches(part, relevant_names, cost)

                        if candidates:
                            self.anchor_method.append("KREISORSTADT")
                            return (part, candidates)

        relevant_names = self.get_loc_names()

        if self.anchor_flag_phonetic:
            for part in parts:
                #candidates_levenshtein = self.get_levenshtein_matches(relevant_names, part, cost)
                candidates_levenshtein = list()
                candidates_phonetic = self.names_by_phonetic.get(self.koelner_phonetic.encode(part), set())
                #candidates_phonetic = list()
                candidates = [*candidates_phonetic, *candidates_levenshtein]

                if candidates:
                    self.anchor_method.append("Phonetic")
                    return (part, candidates)
        
        for cost in range(1, self.levenshtein_max_cost + 1):
            for part in parts:
                candidates = self.get_matches(part, relevant_names, cost)

                if candidates:
                    self.anchor_method.append(f"Cost {cost}")
                    return (part, candidates)
    
        return ("", [])

    def get_matches(self, name: str, relevant_names: set[str], max_cost: int) -> list[str]:
        if self.use_difflib:
            return self.get_difflib_matches(name, relevant_names, max_cost)
        else:
            return self.get_levenshtein_matches(name, relevant_names, max_cost)

    def get_levenshtein_matches(self, name: str, relevant_names: set[str], max_cost: int) -> list[str]:
        lC = LocCorrection.from_list(tuple(relevant_names))
        candidates = lC.search(name, max_cost)

        if candidates:
            best_cost = min(candidates, key=itemgetter(1))[1]
            candidates = [c[0] for c in candidates if c[1] == best_cost]

        return candidates
        
    def get_difflib_matches(self, name: str, relevant_names: set[str], maxcost) -> list[str]:
        return difflib.get_close_matches(name, relevant_names, n=30, cutoff=0.95*(self.levenshtein_max_cost-maxcost)/(self.levenshtein_max_cost-1)+0.6*(maxcost-1)/(self.levenshtein_max_cost-1))

    def get_loc_names(self, type_ids: Optional[set[int]] = None) -> set[str]:
        if type_ids is not None:
            relevant_ids = self.gov.get_ids_by_types(type_ids)
            relevant_names = self.gov.get_names_by_ids(relevant_ids)
        else:
            relevant_names = self.gov.get_loc_names()

        return relevant_names

    def get_relevant_names_from_part_candidates(self, candidates: list[str]) -> set[str]:
        relevant_names = set()
        if candidates:
            ids_for_name = self.gov.get_ids_by_names(candidates)
            ids_for_reachable_nodes = self.gov.get_reachable_nodes_by_id(ids_for_name)
            relevant_names.update(self.gov.get_names_by_ids(ids_for_reachable_nodes))

        return relevant_names

    @staticmethod
    def get_query_parts(query: str) -> tuple[str]:
        """Split Gov item (query) to get the single names (parts)."""
        return tuple(s.strip().lower() for s in query.split(","))
