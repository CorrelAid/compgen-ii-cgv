from pipeline import Pipeline

import pandas as pd


class Baseline(Pipeline):
    def get_matches(self) -> pd.Series:
        matches = self.vl[[f"part_{i}" for i in range(5)]].apply(
            lambda col: (
                col.isin(self.gov_cities.location)
                | col.isin(self.gov_districts.location)
            )
            | col.isna(),
            axis=0,
        )

        self.matches = pd.DataFrame(
            {
                "location": self.vl.location,
                "id": matches.all(axis=1).replace(False, ""),
                "score": matches.all(axis=1).astype(int),
            }
        )


if __name__ == "__main__":
    p = Baseline()
    p.run()
