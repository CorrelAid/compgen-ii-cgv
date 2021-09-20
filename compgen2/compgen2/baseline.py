import pandas as pd
from tqdm import tqdm

from .pipeline import Pipeline


class Baseline(Pipeline):
    """Use GOV and Matcher to calculate a simple baseline

    The simple baseline only returns a textual ID for these items
        that have a unique match.
    """

    def get_matches_by_path(self) -> pd.Series:
        def get_textual_id(query: str):
            paths = self.matcher.find_relevant_paths(query)
            grouped_paths = self.matcher.group_relevant_paths_by_query(paths, query)

            textual_id = ""
            if len(grouped_paths) == 1:
                textual_id = grouped_paths[0]["lower_level_textual_id"]

            return textual_id

        matches = [
            get_textual_id(query)
            for query in tqdm(self.vl.location, desc="VL entry", position=0, leave=True)
        ]

        self.matches = pd.DataFrame(
            {
                "location": self.vl.location,
                "id": matches,
                "score": [1 if x != "" else 0 for x in matches],
            }
        )

    def get_matches(self) -> pd.Series:
        def get_textual_id(query: str):
            relevant_ids = self.matcher.find_relevant_ids(query)

            textual_id = ""
            if len(relevant_ids) == 1:
                ids = relevant_ids[0]
                lower_id = min(
                    ids, key=lambda id_: len(self.gov.all_reachable_nodes_by_id[id_])
                )
                textual_id = self.gov.items.query("id == @lower_id").textual_id.values[
                    0
                ]

            return textual_id

        matches = [
            get_textual_id(query) for query in tqdm(self.vl.location, desc="VL entry")
        ]
        print(matches)

        self.matches = pd.DataFrame(
            {
                "location": self.vl.location,
                "id": matches,
                "score": [1 if x != "" else 0 for x in matches],
            }
        )

    def get_matches_alt(self) -> pd.Series:
        matches = []
        scores = []
        for name in tqdm(self.vl.location, desc="VL entry"):
            relevant_ids = self.matcher.find_relevant_ids(name)
            matches.append(1 if relevant_ids else 0)
            scores.append(1 / len(relevant_ids) if relevant_ids else 0)

        self.matches = pd.DataFrame(
            {
                "location": self.vl.location,
                "id": matches,
                "score": matches,
            }
        )


if __name__ == "__main__":
    p = Baseline()
    p.run()
