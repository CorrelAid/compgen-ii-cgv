from .gov_extraction import GOV


class Matcher:
    def __init__(self, gov: GOV) -> None:
        self.gov = gov

        print(f"Initialized matcher with a gov database of {len(gov.items):,} items.")

    def find_relevant_paths(self, entry: str) -> set[tuple[int, ...]]:
        """Retrieve all paths from GOV where entry is part of the path.

        Entry can have multiple 'parts' which are separated by ','. 
            Each part must be part of the path to be a valid match.

        Args:
            entry (str): GOV item name, as defined in gov_a_propertynames.csv. 
                For example "Aachen, Freudenstadt".

        Returns:
            set[tuple[int, ...]]: The relevant paths from GOV that matched the entry.
        """
        paths = self.gov.all_paths()
        parts = [s.strip() for s in entry.split(",")]

        search_ids_by_part = [
            set(self.gov.get_all_ids_for_name(name)) for name in parts
        ]

        return {
            path
            for path in paths
            if all(set(path) & search_ids for search_ids in search_ids_by_part)
        }
