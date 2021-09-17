from collections import defaultdict
from itertools import product
from typing import Union

from .gov_extraction import GOV


class Matcher:
    def __init__(self, gov: GOV) -> None:
        self.gov = gov

        print(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

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
        paths = self.gov.all_paths()
        parts = Matcher.get_query_parts(query)
        search_ids_by_part = self.get_ids_by_part(parts)

        return {
            path
            for path in paths
            if all(set(path) & search_ids for search_ids in search_ids_by_part.values())
        }

    def group_relevant_paths_by_query(
        self, paths: set[tuple[int, ...]], query: str
    ) -> dict[str, Union[int, set[tuple[int, ...]]]]:
        """Take the result of `find_relevant_paths` and group by part ids.

        Args:
            paths (set[tuple[int, ...]]): Result of `find_relevant_paths`.
            query (str): GOV item name, as defined in gov_a_propertynames.csv.
                For example "Aachen, Freudenstadt".

        Returns:
            dict[str, Union[int, set[tuple[int, ...]]]]:
                A dictionary with the tuple of part ids as key and the relevant paths as value.
        """
        parts = Matcher.get_query_parts(query)
        search_ids_by_part = self.get_ids_by_part(parts)

        # iterate each possible pair of ids
        # and group all paths by this pair
        matches = []
        for ids in product(*search_ids_by_part.values()):
            paths_containing_ids = set()
            for path in paths:
                if set(path).issuperset(ids):
                    paths_containing_ids.add(path)

            if paths_containing_ids:
                match = {name: id_ for name, id_ in zip(parts, ids)}
                match["paths"] = paths_containing_ids
                matches.append(match)

        return matches

    def get_ids_by_part(self, parts: tuple) -> dict[str, set]:
        """Return all ids for each name (part) of a GOV item."""
        return dict((name, set(self.gov.get_all_ids_for_name(name))) for name in parts)

    @staticmethod
    def get_query_parts(query: str) -> tuple:
        """Split GOV item (query) to get the single names (parts)."""
        return tuple(s.strip() for s in query.split(","))
