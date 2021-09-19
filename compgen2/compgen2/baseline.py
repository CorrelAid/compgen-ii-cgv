import pandas as pd
from tqdm import tqdm

from .pipeline import Pipeline


class Baseline(Pipeline):
    """Use GOV and Matcher to calculate a simple baseline
    
    The simple baseline only returns a textual ID for these items
        that have a unique match.
    """
    def get_matches(self) -> pd.Series:

        def get_textual_id(query: str):
            paths = self.matcher.find_relevant_paths(query)
            grouped_paths = self.matcher.group_relevant_paths_by_query(paths, query)
            
            textual_id = ""
            if len(grouped_paths) == 1:
                textual_id = grouped_paths[0]["lower_level_textual_id"]
            
            return textual_id            

        matches = [get_textual_id(query) for query in tqdm(self.vl.location, desc="VL entry")]

        self.matches = pd.DataFrame(
            {
                "location": self.vl.location,
                "id": matches,
                "score": [1 if x != "" else 0 for x in matches],
            }
        )


if __name__ == "__main__":
    p = Baseline()
    p.run()
