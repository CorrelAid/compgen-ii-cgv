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
        self.matches = pd.Series(dtype='object')
        self.hash = b""
        self.version = 1

    def run(self):
        self.hash = self.__get_pipeline_hash()
        self.__prepare_pipeline()

        self.load_data()
        self.preprocess()
        self.get_matches()
        self.evaluate()
        self.output()

    def __prepare_pipeline(self):
        pipeline_dir = Pipeline.dir_log / "pipeline"
        pipeline_dir.mkdir(parents=True, exist_ok=True)

        # load last model, if it exists, and compare hashes
        # if Pipeline has changed, increment version counter
        if list(pipeline_dir.glob(f"{self.__class__.__name__}*.pickle")):
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
        """ load important data like Verlustliste and GOV lists
        
        Here you can set self.vl, self.gov_cities and self.gov_districts
        """
        self.vl = Pipeline.read_vl(Pipeline.dir_vl)
        self.gov_cities = Pipeline.read_gov(Pipeline.dir_gov_cities)
        self.gov_districts = Pipeline.read_gov(Pipeline.dir_gov_districts)
        

    def preprocess(self):
        """ preprocess data to improve performance of matching algorithm 
        
        Here you can alter self.vl, self.gov_cities and self.gov_districts
        """
        pass

    def get_matches(self) -> pd.Series:
        """ Get match for each entry of self.vl
        
        Here you can implement the matching algorithm. 
        
        Returns:
               (pd.Series): A Series with self.vl.location as index and the Gov ID as value 
        """
        self.matches = pd.Series("", index=self.vl.location)
        
    def evaluate(self) -> tuple[int, int]:
        """ Evaluate the results of the matching algorithm 
        
        Here you can evaluate the performance of the matching algorithm
        
        Returns: 
            (tuple[int, float]): tuple of two values:absolute number of matches and relative number of non matches
        """
        nr_matches = len(self.matches) - sum(self.matches.eq(""))
        return nr_matches, nr_matches / len(self.matches)
        
            
    def output(self):
        """ Append results to the pipeline log """
        output_file = Pipeline.dir_log.joinpath(self.get_pipeline_name() + ".log")
        with open(output_file, "a", encoding="utf-8") as stream:
            stream.write(str(self))
            stream.write("\n")
            
        output_file = Pipeline.dir_log.joinpath(self.get_pipeline_name() + "_matches.csv")
        self.matches.name = "ID"
        self.matches.index.name = "location"
        self.matches.to_csv(output_file)
        
    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} version {self.version} | vl: {len(self.vl):,} lines"
            f" | gov cities: {len(self.gov_cities):,} lines"
            f" | gov districts: {len(self.gov_districts):,} lines"
            f" | matches: {self.evaluate()[0]:,} ({self.evaluate()[1]:.2f})"
        )
    
    def get_pipeline_name(self) -> str:
        return f"{self.__class__.__name__.lower()}_v{self.version:02}"
                 
    def __get_pipeline_hash(self) -> bytes:
        m = hashlib.sha256()
        m.update(inspect.getsource(self.__class__).encode())
        
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
