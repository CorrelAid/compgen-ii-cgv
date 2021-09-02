from pipeline import Pipeline

import pandas as pd


class Baseline(Pipeline):

    def get_matches(self) -> pd.Series:
        matches = self.vl.location.str.split(",", expand=True)[0].isin(
            self.gov_cities.append(self.gov_districts).location
        )
        
        self.matches = pd.Series(matches.replace(False, ""), index=self.vl.index)


if __name__ == "__main__":
    p = Baseline()
    p.run()
