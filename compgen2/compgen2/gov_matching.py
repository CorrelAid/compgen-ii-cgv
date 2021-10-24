import logging
from itertools import product
from typing import Optional

from tqdm import tqdm

from .const import T_KREISUNDHOEHER, T_STADT
from .gov_extraction import GOV
from .loc_autocorrection import LocCorrection

logger = logging.getLogger(__name__)
MAX_COST_EXPENSIVE = 5
MAX_COST_INEXPENSIVE = 10


class Matcher:
    def __init__(self, gov: GOV) -> None:
        self.gov = gov
        self.results = {}

        if not self.gov.fully_initialized:
            logger.warning(
                "Passed instance of gov is not fully initialized. "
                "Make sure to run `load_data()` and `build_indices()`."
            )
        else:
            logger.info(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

    def get_match_for_locations(self, locations: list[str]) -> None:
        self.find_parts_for_location(locations)
        self.find_textual_id_for_location()

    def find_parts_for_location(self, locations: list[str]) -> None:
        """Find the GOV parts for each location name.

        If a part is not found in the GOV in its original form, we try to find better candidates.
            Candidates are found by using the Levenshtein distance.

        This method fills the 'parts' dictionary of self.result[location].
            For each part of location, there will be a new entry with
                - in_gov (bool): True, if part is part of GOV, False otherwise.
                - candidates (list): A list of possible candidates in GOV.

        Args:
            locations (list[str]): list of location names, e.g. "aachen, alsdorf".
        """
        for location in tqdm(locations, desc="Find parts for location"):
            self.results[location] = {"parts": {}}
            parts = Matcher.get_query_parts(location)
            for part in parts:
                in_gov = True if part in self.gov.ids_by_name else False
                self.results[location]["parts"][part] = {
                    "in_gov": in_gov,
                    "candidates": [part] if in_gov else [],
                }

            # first handle case that we did not find anything for any part
            # try to find at least one candidate for any part
            if not any(part["in_gov"] for part in self.results[location]["parts"].values()):
                matched_part, candidates = self.find_part_with_best_candidates(parts)

                if candidates:
                    self.results[location]["parts"][matched_part]["candidates"].extend(c[0] for c in candidates)

            # now check if there is still one part without a match
            # and use the already matched part to get relevant names
            for unmatched_part in parts:
                if (
                    not self.results[location]["parts"][unmatched_part]["in_gov"]
                    and not self.results[location]["parts"][unmatched_part]["candidates"]
                ):
                    relevant_names = set()
                    for matched_part in parts:
                        if unmatched_part == matched_part:
                            continue

                        candidates = self.results[location]["parts"][matched_part]["candidates"]
                        relevant_names.update(self.get_relevant_names_from_part_candidates(candidates))

                    candidates = self.get_best_candidates(relevant_names, unmatched_part, MAX_COST_INEXPENSIVE)
                    self.results[location]["parts"][unmatched_part]["candidates"].extend(c[0] for c in candidates)

    def find_textual_id_for_location(self) -> None:
        """Find a textual id for each location name."""
        for location in self.results:
            self.results[location]["possible_matches"] = []

            list_of_candidates = [
                part["candidates"] for part in self.results[location]["parts"].values() if part["candidates"]
            ]

            if list_of_candidates:
                for combination_of_names in product(*list_of_candidates):
                    ids_for_combination = (self.gov.ids_by_name[name] for name in combination_of_names)
                    for ids in product(*ids_for_combination):
                        if len(ids) > 1:
                            if not self.gov.all_reachable_nodes_by_id[ids[0]].issuperset(ids[1:]):
                                continue

                        textual_ids = [self.gov.items_by_id[id_] for id_ in ids]
                        type_ids = list(set().union(*(self.gov.types_by_id[id_] for id_ in ids)))
                        type_names = [self.gov.type_names_by_type[type_id] for type_id in type_ids]
                        match = {
                            "parts": list(combination_of_names),
                            "gov_ids": ids,
                            "textual_ids": textual_ids,
                            "type_ids": type_ids,
                            "type_names": type_names,
                        }
                        self.results[location]["possible_matches"].append(match)

    def find_part_with_best_candidates(self, parts: tuple[str]) -> tuple[str, list[tuple[str, int]]]:
        for type_ids in [T_KREISUNDHOEHER, T_STADT]:
            for cost in range(1, MAX_COST_EXPENSIVE + 1):
                for part in parts:                    
                    relevant_names = self.get_loc_names(type_ids)
                    candidates = self.get_best_candidates(relevant_names, part, cost)

                    if candidates:
                        return (part, candidates)

        # if nothing could be found in kreis or higher, broaden search by using complete GOV
        for part in parts:
            relevant_names = self.get_loc_names()
            candidates = self.get_best_candidates(relevant_names, part, MAX_COST_EXPENSIVE)

            if candidates:
                return (part, candidates)

        return ("", [])

    def get_best_candidates(self, relevant_names: set[str], name: str, cost: int) -> list[tuple[str, int]]:
        relevant_names = filter_relevant_names(relevant_names, name, cost)
        lC = LocCorrection.from_list(tuple(relevant_names))
        return lC.get_best_candidates(name, cost)

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

    def find_relevant_ids(self, query: str) -> list[tuple[int, ...]]:
        """Retrieve all ids from GOV where the query is part of the path."""
        parts = Matcher.get_query_parts(query)
        ids_by_part = self.get_ids_by_part(parts)

        if not any(ids_by_part.values()):
            return []

        if len(parts) == 1:
            return [(x,) for x in ids_by_part[parts[0]]]

        relevant_ids = [
            ids
            for ids in product(*ids_by_part.values())
            if self.gov.all_reachable_nodes_by_id[ids[0]].issuperset(ids[1:])
        ]

        return relevant_ids

    @staticmethod
    def get_query_parts(query: str) -> tuple[str]:
        """Split GOV item (query) to get the single names (parts)."""
        return tuple(s.strip().lower() for s in query.split(","))


def filter_relevant_names(relevant_names: set[str], query: str, max_cost: int) -> set[str]:
    return set(name for name in relevant_names if len(query) - max_cost <= len(name) <= len(query) + max_cost)
