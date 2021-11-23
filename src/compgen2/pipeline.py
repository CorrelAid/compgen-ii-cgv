"""Main Pipeline class to match entries of VL against GOV

How to use:
```
p = Pipeline(<data_root>)
p.run()
```
"""
import hashlib
import inspect
import logging
import pickle
from pathlib import Path

import pandas as pd

from .const import LOG_PATH, FILENAME_VL
from .gov import Gov, Matcher
from .correction import Preprocessing_VL, Preprocessing_GOV

logger = logging.getLogger(__name__)


class Pipeline:
    """Base class for building a data science pipeline for the compgen2 project."""

    def __init__(self, data_root: str) -> None:
        self.data_root = Path(data_root)
        
        if self.data_root.joinpath("gov.pickle").exists():
            logger.info("Found serialized gov object.")
            self.gov = GOV.from_file(self.data_root / "gov.pickle")
        else:
            self.gov = GOV(data_root)
            
        self.matcher = Matcher(self.gov)

        self.vl = pd.DataFrame()
        self.matches = pd.DataFrame()  # a df with three columns for location, textual_id and score
        self.hash = b""
        self.version = 1

    def run(self):
        self.hash = self.__get_pipeline_hash()
        self.__prepare_pipeline()

        logger.info("Loading data...")
        self.load_data()
        assert not self.vl.empty
        assert not self.gov.items.empty

        logger.info("Preprocessing data...")
        self.preprocess()
        self.gov.build_indices()

        logger.info("Matching data with gov...")
        self.get_matches()
        assert not self.matches.empty
        assert self.matches.shape[1] == 3  # should be a data frame with 3 columns
        assert len(self.matches) == len(self.vl)  # should have the same length like vl

        logger.info("Saving pipeline and data to ./log...")
        self.output()

    def __prepare_pipeline(self):
        pipeline_dir = Path(LOG_PATH) / "pipeline"
        pipeline_dir.mkdir(parents=True, exist_ok=True)

        # load last model, if it exists, and compare hashes
        # if Pipeline has changed, increment version counter
        if list(pipeline_dir.glob(f"{self.__class__.__name__}*.pickle")):
            last_model_path = list(pipeline_dir.glob("*.pickle"))[-1]
            with open(last_model_path, "rb") as stream:
                last_model: Pipeline = pickle.load(stream)

            if last_model.hash != self.hash:
                self.version = last_model.version + 1

    def load_data(self) -> None:
        """Load important data.

        Loads Verlustliste and GOV data tables.
        """
        self.gov.load_data()
        self.vl = self.read_vl()

    def read_vl(self) -> pd.DataFrame:
        path = self.data_root / FILENAME_VL
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

    def preprocess(self) -> None:
        """preprocess data to improve performance of matching algorithm

        Here you can alter self.vl, and all data stored in self.gov
        """
        self.vl = Preprocessing.prep_clean_brackets(self.vl) # clean bracket
        # optional:  self.vl = prep_clean_korrigiert(self.vl) 
        self.vl = Preprocessing.prep_clean_characters(self.vl) # clean characters  
        self.vl = Preprocessing.prep_vl_abbreviations(self.vl) # substitute abbreviations

    def get_matches(self) -> None:
        """Get match for each entry of self.vl

        Here you can implement the matching algorithm.
        """
        self.matches = self.matcher.get_match_for_locations(self.vl.location.values.tolist())

    def evaluate(self) -> tuple[int, int]:
        """Evaluate the results of the matching algorithm

        Here you can evaluate the performance of the matching algorithm

        Returns:
            (tuple[int, float]): tuple of two values: absolute and relative number of matches
        """
        nr_matches = len(self.matches) - sum(self.matches["id"].eq(""))
        return nr_matches, nr_matches / len(self.matches)

    def output(self) -> None:
        """Append results to the pipeline log"""
        logger.info(str(self))

        output_file = Path(LOG_PATH).joinpath(self.get_pipeline_name() + ".log")
        with open(output_file, "a", encoding="utf-8") as stream:
            stream.write(str(self))
            stream.write("\n")

        output_file = Path(LOG_PATH).joinpath(self.get_pipeline_name() + "_matches.csv")
        self.matches.to_csv(output_file, index=False)

        # pickle pipeline
        self.vl = pd.DataFrame()
        self.matches = pd.DataFrame()
        self.gov.clear_data()
        pipeline_dir = Path(LOG_PATH) / "pipeline"
        with open(
            pipeline_dir.joinpath(self.get_pipeline_name() + ".pickle"), "wb"
        ) as stream:
            pickle.dump(self, stream, pickle.HIGHEST_PROTOCOL)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} version {self.version} | vl: {len(self.vl):,} lines"
            f" | gov: {len(self.gov.names.id.unique()):,} unique IDs"
            f" | matches: {self.evaluate()[0]:,} ({self.evaluate()[1]:.2f})"
        )

    def get_pipeline_name(self) -> str:
        return f"{self.__class__.__name__.lower()}_v{self.version:02}"

    def __get_pipeline_hash(self) -> bytes:
        """Update the hash whenever the source code of Pipeline, GOV or Matcher is changed."""
        m = hashlib.sha256()
        m.update(inspect.getsource(self.__class__).encode())
        m.update(inspect.getsource(self.gov.__class__).encode())
        m.update(inspect.getsource(self.matcher.__class__).encode())

        return m.digest()
