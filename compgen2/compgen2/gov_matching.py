from itertools import product

import numpy as np

from .gov_extraction import GOV


class Matcher:
    def __init__(self, gov: GOV) -> None:
        self.gov = gov

        print(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

    def find_relevant_ids(self, query: str) -> list[tuple[int, ...]]:
        """Retrieve all ids from GOV where the query is part of the path."""
        parts = Matcher.get_query_parts(query)
        search_ids_by_part = self.get_ids_by_part(parts)

        if any(not ids for ids in search_ids_by_part):
            return []

        if len(parts) == 1:
            return [(x,) for x in search_ids_by_part[0]]

        relevant_ids = [
            ids
            for ids in product(*search_ids_by_part)
            if self.gov.all_reachable_nodes_by_id[ids[0]].issuperset(ids[1:])
        ]

        return relevant_ids

    def find_relevant_paths(self, query: str) -> set[tuple[int, ...]]:
        """Retrieve all paths from GOV where query is part of the path.

        The query can have multiple 'parts' which are separated by ','.
            Each part must be part of the path to be a valid match.

        Args:
            query (str): GOV item name, as defined in gov_a_propertynames.csv.
                For example "Aachen, Freudenstadt".

        Returns:
            set[tuple[int, ...]]: The relevant paths from GOV that matched the query.
        """
        parts = Matcher.get_query_parts(query)
        search_ids_by_part = self.get_ids_by_part(parts)

        if any(not ids for ids in search_ids_by_part):
            return set()

        return {
            path
            for path in self.gov.all_paths
            if all(set(path) & search_ids for search_ids in search_ids_by_part)
        }

    def group_relevant_paths_by_query(
        self, paths: set[tuple[int, ...]], query: str
    ) -> list[dict]:
        """Take the result of `find_relevant_paths` and group by part ids.

        Args:
            paths (set[tuple[int, ...]]): Result of `find_relevant_paths`.
            query (str): GOV item name, as defined in gov_a_propertynames.csv.
                For example "Aachen, Freudenstadt".

        Returns:
            list[dict]:
                A list of dictionaries. Each dictionary contains the relevant paths for one particular combination of ids.
        """
        if not paths:
            return []

        parts = Matcher.get_query_parts(query)
        search_ids_by_part = self.get_ids_by_part(parts)

        # iterate each possible pair of ids
        # and group all paths by this pair
        matches = []
        for ids in product(*search_ids_by_part):
            paths_containing_ids = set()
            for path in paths:
                if set(path).issuperset(ids):
                    paths_containing_ids.add(path)

            if paths_containing_ids:
                match = {name: id_ for name, id_ in zip(parts, ids)}
                lower_level_id = ids[np.argmax(ids.index(i) for i in ids)]
                match["lower_level_id"] = lower_level_id
                match["lower_level_textual_id"] = self.gov.items.query(
                    "id == @lower_level_id"
                ).textual_id.values[0]
                match["paths"] = paths_containing_ids
                matches.append(match)

        return matches

    def get_ids_by_part(self, parts: tuple) -> tuple[set[int]]:
        """Return all ids for each name (part) of a GOV item."""
        return tuple(self.gov.ids_by_name.get(name, set()) for name in parts)

    @staticmethod
    def get_query_parts(query: str) -> tuple[str]:
        """Split GOV item (query) to get the single names (parts)."""
        return tuple(s.strip() for s in query.split(","))
