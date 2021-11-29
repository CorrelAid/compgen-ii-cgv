"""This module contains the Matcher class that provides the main logic to match names against the Gov database.

Examples:
```Python
m = Matcher(gov)
m.get_match_for_locations(["Aachen", "aarösund, flensburg"])
print(m.results)
```
"""
import difflib
import logging
from itertools import product
from operator import itemgetter
from typing import Optional, Union

import pandas as pd
from tqdm import tqdm

from .. import LocCorrection, Phonetic
from ..const import T_KREISUNDHOEHER, T_STADT
from . import Gov

logger = logging.getLogger(__name__)


class Matcher:
    """Main class to match names against the Gov database.

    Main steps of the matching algorithm:
        1. ...

    Attributes:
        gov (Gov): A fully initialized instance of the Gov class.
        koelner_phonetic (Phonetic): Instance of Phonetic class.
        use_difflib (bool): If True, uses difflib.get_close_matches to find candidates.
        use_phonetic (bool): If True, uses Koelner Phonetic to search for candidates.
        max_cost (int): Max cost for searching for candidates. Value between 1 and max_cost.
        search_kreis_first (bool): If True, searches for candidates in Kreis or higher first.
        results (dict): A dictionary containing the final results.
            Provides information about the found parts and the possible matches for each query.

    """

    def __init__(
        self,
        gov: Gov,
        use_difflib: bool = True,
        use_phonetic: bool = False,
        max_cost: int = 3,
        search_kreis_first: bool = False,
    ) -> None:
        self.gov = gov

        if not self.gov.fully_initialized:
            logger.warning(
                "Passed instance of gov is not fully initialized. "
                "Make sure to run `load_data()` and `build_indices()`."
            )
        else:
            logger.info(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

        self.use_difflib = use_difflib
        self.use_phonetic = use_phonetic
        self.max_cost = max_cost
        self.search_kreis_first = search_kreis_first
        self.results = {}

        self.koelner_phonetic = Phonetic()
        if self.use_phonetic:
            self.koelner_phonetic.build_phonetic_index(gov.get_loc_names())

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
                "anchor": in_gov,
            }

        matched_parts = self.get_matched_parts(location)
        if len(matched_parts) == len(parts):
            self._set_anchor_method_for_location(location, "gov complete")
            return

        # first handle case that we did not find anything for any part
        # try to find at least one candidate for any part
        if not matched_parts:
            matched_part, candidates = self.find_part_with_best_candidates(location, parts)

            if candidates:
                self.results[location]["parts"][matched_part]["candidates"].extend(candidates)
                self.results[location]["parts"][matched_part]["anchor"] = True
            else:
                self._set_anchor_method_for_location(location, "No anchor at all")
        else:
            self._set_anchor_method_for_location(location, "gov partial")

        # now check if there is still unmatched parts
        # and use the already matched part to get relevant names
        unmatched_parts = self.get_unmatched_parts(location)
        matched_parts = self.get_matched_parts(location)
        if unmatched_parts and matched_parts:
            relevant_names = self.get_relevant_names_from_matched_parts(location)
            for unmatched_part in [
                part for part, partdict in self.results[location]["parts"].items() if not partdict["candidates"]
            ]:
                candidates = self.get_matches(unmatched_part, relevant_names, self.max_cost)
                self.results[location]["parts"][unmatched_part]["candidates"].extend(candidates)
                
    def find_textual_id_for_location(self, location: str) -> None:
        """Find a textual id for given location name."""

        self.results[location]["possible_matches"] = []

        # ignore parts with no candidates so we still find partial matches
        list_of_candidates = [
            part["candidates"] for part in self.results[location]["parts"].values() if part["candidates"]
        ]

        if list_of_candidates:
            for combination_of_names in product(*list_of_candidates):
                ids_for_combination = (self.gov.ids_by_name[name] for name in combination_of_names)
                for ids in product(*ids_for_combination):
                    if len(ids) > 1:
                        # TODO: what to do if items exist in Gov but not the relationship?
                        highest_id = max(ids, key=lambda x: len(self.gov.all_reachable_nodes_by_id[x]))
                        other_ids = {id_ for id_ in ids if id_ != highest_id}
                        if not self.gov.all_reachable_nodes_by_id[highest_id].issuperset(other_ids):
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
                            "type_names": type_names,
                        }

                    self.results[location]["possible_matches"].append(match)

    def find_part_with_best_candidates(self, location: str, parts: tuple[str]) -> tuple[str, list[str]]:
        if self.use_phonetic:
            for part in parts:
                candidates = list(
                    self.koelner_phonetic.names_by_phonetic.get(self.koelner_phonetic.encode(part), set())
                )

                if candidates:
                    self._set_anchor_method_for_location(location, f"Phonetic")
                    return (part, candidates)
                
        if self.search_kreis_first:
            for type_ids in [T_KREISUNDHOEHER, T_STADT]:
                for cost in range(1, 3 + 1):
                    for part in parts:
                        relevant_names = self.get_loc_names(type_ids)
                        candidates = self.get_matches(part, relevant_names, cost)

                        if candidates:
                            self._set_anchor_method_for_location(location, f"KREISORSTADT | Cost {cost}")
                            return (part, candidates)

        relevant_names = self.get_loc_names()
        for cost in range(1, self.max_cost + 1):
            for part in parts:
                candidates = self.get_matches(part, relevant_names, cost)

                if candidates:
                    self._set_anchor_method_for_location(location, f"ALL GOV | Cost {cost}")
                    return (part, candidates)

        return ("", [])

    def get_matches(self, name: str, relevant_names: set[str], cost: int) -> list[str]:
        if self.use_difflib:
            return self.get_difflib_matches(name, relevant_names, cost)
        else:
            return self.get_levenshtein_matches(name, relevant_names, cost)

    def get_levenshtein_matches(self, name: str, relevant_names: set[str], cost: int) -> list[str]:
        lC = LocCorrection.from_list(tuple(relevant_names))
        candidates = lC.search(name, cost)

        if candidates:
            best_cost = min(candidates, key=itemgetter(1))[1]
            candidates = [c[0] for c in candidates if c[1] == best_cost]

        return candidates

    def get_difflib_matches(self, name: str, relevant_names: set[str], cost) -> list[str]:
        return difflib.get_close_matches(
            name,
            relevant_names,
            n=30,
            cutoff=0.90 - (0.90 - 0.6) * (cost - 1) / (self.max_cost - 1),
        )

    def get_loc_names(self, type_ids: Optional[set[int]] = None) -> set[str]:
        if type_ids is not None:
            relevant_ids = self.gov.get_ids_by_types(type_ids)
            relevant_names = self.gov.get_names_by_ids(relevant_ids)
        else:
            relevant_names = self.gov.get_loc_names()

        return relevant_names

    def get_relevant_names_from_matched_parts(self, location: str) -> set[str]:
        matched_parts = self.get_matched_parts(location)
        
        if not matched_parts:
            return set()
        
        relevant_ids = set()

        # for each part, get all ids for all reachable nodes
        # then use only the intersection between different parts as search space
        for part in matched_parts:
            ids_for_name = self.gov.get_ids_by_names(self.get_part_candidates(location, part)) 
            ids_for_reachable_nodes = self.gov.get_reachable_nodes_by_id(ids_for_name)
            relevant_ids.update(ids_for_reachable_nodes)

        return self.gov.get_names_by_ids(relevant_ids)

    @staticmethod
    def get_query_parts(query: str) -> tuple[str]:
        """Split Gov item (query) to get the single names (parts)."""
        return tuple(s.strip().lower() for s in query.split(","))

    def _set_anchor_method_for_location(self, location: str, method: str):
        self.results[location]["anchor_method"] = method

    def get_matched_parts(self, location: str) -> list[str]:
        return [part for part, partdict in self.results[location]["parts"].items() if partdict["candidates"]]

    def get_unmatched_parts(self, location: str) -> list[str]:
        return [part for part, partdict in self.results[location]["parts"].items() if not partdict["candidates"]]
    
    def get_part_candidates(self, location, part) -> list[str]:
        return self.results[location]["parts"][part]["candidates"]