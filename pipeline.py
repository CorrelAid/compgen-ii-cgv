import hashlib
import inspect
import pickle
from pathlib import Path

import pandas as pd


class Pipeline:

    dir_vl = Path("data/deutsche-verlustlisten-1wk.tsv")
    dir_gov_cities = Path("data/gov_orte_v01.csv")
    dir_gov_districts = Path("data/gov_kreise_v01.csv")
    dir_log = Path("log/")

    def __init__(self) -> None:
        self.vl = pd.DataFrame()
        self.gov_cities = pd.DataFrame
        self.gov_districts = pd.DataFrame()
        self.matches = pd.Series()
        self.hash = b""
        self.version = 1

    def run(self):
        self.hash = Pipeline.get_pipeline_hash()
        self.prepare_pipeline()

        self.load_data()
        self.preprocess()
        self.get_matches()
        self.evaluate()

    def prepare_pipeline(self):
        pipeline_dir = Pipeline.dir_log / "pipeline"
        pipeline_dir.mkdir(parents=True, exist_ok=True)

        # load last model, if it exists, and compare hashes
        # if Pipeline has changed, increment version counter
        if list(pipeline_dir.glob("*.pickle")):
            last_model_path = list(pipeline_dir.glob("*.pickle"))[-1]
            with open(last_model_path, "rb") as stream:
                last_model: Pipeline = pickle.load(stream)
                
            if last_model.hash != self.hash:
                self.version = last_model.version + 1

        with open(
            pipeline_dir.joinpath(self.get_pipeline_name() + ".pickle"), "wb"
        ) as stream:
            pickle.dump(self, stream, pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        self.vl = Pipeline.read_vl(Pipeline.dir_vl)
        self.gov_cities = Pipeline.read_gov(Pipeline.dir_gov_cities)
        self.gov_districts = Pipeline.read_gov(Pipeline.dir_gov_districts)

    def preprocess(self):
        pass

    def get_matches(self):
        self.matches = self.vl.location.str.split(",", expand=True)[0].isin(
            self.gov_cities.append(self.gov_districts).location
        )
        
    def evaluate(self):
        output_file = Pipeline.dir_log.joinpath(self.get_pipeline_name() + ".log")
        with open(output_file, "a", encoding="utf-8") as stream:
            stream.write(str(self))
            stream.write("\n")
        
    def __str__(self) -> str:
        return (
            f"Pipeline version {self.version} | vl: {len(self.vl):,} lines"
            f" | gov cities: {len(self.gov_cities):,} lines"
            f" | gov districts: {len(self.gov_districts):,} lines"
            f" | matches: {sum(self.matches):,} ({sum(self.matches) / len(self.vl):,})"
        )
    
    def get_pipeline_name(self) -> str:
        return f"pipeline_v{self.version:02}"
    
    @classmethod             
    def get_pipeline_hash(cls) -> bytes:
        m = hashlib.sha256()
        m.update(inspect.getsource(cls).encode())
        
        return m.digest()

    @staticmethod
    def read_vl(path) -> pd.DataFrame:
        parquet_filename = path.parent / (
            path.stem + ".parquet"
        )  # replace .csv with .parquet

        def get_location_parts_count(loc):
            return len(loc.split(","))

        # read in tsv and save as parquet, if not already done
        if not Path(parquet_filename).exists():
            vl = pd.read_csv(
                path, sep="\t", header=None, names=["loc_count", "location"]
            )
            vl = vl[~vl.location.isna()]
            vl = vl.assign(loc_parts_count=vl.location.map(get_location_parts_count))
            vl.to_parquet(parquet_filename)

        return pd.read_parquet(parquet_filename)

    @staticmethod
    def read_gov(path) -> pd.DataFrame:
        parquet_filename = path.parent / (
            path.stem + ".parquet"
        )  # replace .csv with .parquet

        # read in csv and save as parquet, if not already done
        if not Path(parquet_filename).exists():
            gov = pd.read_csv(path, sep="\t", header=None, names=["id", "location"])
            gov.to_parquet(parquet_filename)

        return pd.read_parquet(parquet_filename)


if __name__ == "__main__":
    p = Pipeline()
    p.run()
