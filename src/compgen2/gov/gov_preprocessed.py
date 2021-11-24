"""This module contains the Gov class that provides an interface to all data in the Gov database.

Examples:
```Python
# first, initialize the instance properly
gov = Gov(data_root)
gov.load_data()
gov.build_indices()

# now you can call any gov method.
gov.all_paths()
```
"""
import logging
import pickle
from collections import defaultdict
from functools import lru_cache
## Imports
from pathlib import Path

import numpy as np
import pandas as pd

from compgen2.gov.gov import Gov

from ..const import *

logger = logging.getLogger(__name__)

class GovPreprocessed:
    """Preprocessed class to work with Gov items.
    """

    def __init__(self, gov: Gov) -> None:
        self.gov = gov

        # gov constants
        self.data_root = gov.data_root
        self.fully_initialized = gov.fully_initialized

        # gov search indices
        self.items_by_id = gov.items_by_id
        self.types_by_id = gov.types_by_id
        self.names_by_id = dict()
        self.ids_by_name = dict()
        self.ids_by_type = gov.ids_by_type
        self.type_names_by_type = gov.type_names_by_type
        self.all_relations = gov.all_relations
        self.all_paths = gov.all_paths
        self.all_reachable_nodes_by_id = gov.all_reachable_nodes_by_id
        self.years = gov.years

        logger.info("Initialized empty gov instance. Please call `load_data()` next.")

    def preprocess_names(self):
        self.ids_by_name = self.gov.names_by_id # DUMMY code - the actual preprocessing has to be integrated here!!!
        self.names_by_id = self.gov.ids_by_name # DUMMY code - the actual preprocessing has to be integrated here!!!

    def build_indices(self):
        """Build all relevant indices that are necessary for efficiently querying and working with Gov."""
        if self.fully_initialized:
            return
        
        self.gov.build_indices()

        logger.info("Finished building all relevant search indices. You can now start working with Gov data.")

    def clear_data(self):
        """Necessary step to pickle model so that its size its manageable.

        If you unpickle a pipeline object you will have to call `load_data()` and `build_indices()` again.
        """
        self.gov.clear_data()

    @lru_cache
    def get_loc_names(self) -> set[str]:
        """Return all location names stored in Gov

        Returns:
            set[str]: set of names
        """
        return self.gov.get_loc_names()

    def decode_path_id(self, path: tuple[int]) -> tuple[int]:
        """Return the gov textual id for each node in a path."""
        return self.gov.decode_path_id(path)

    def decode_path_name(self, path: tuple[int]) -> tuple[str]:
        """Return the gov display name for each node in a path."""
        return self.gov.decode_path_name(path)

    def decode_path_type(self, path: tuple[int]) -> tuple[int]:
        """Return the type display name for each node in a path."""
        return self.gov.decode_path_type(path)

    def get_ids_by_types(self, type_ids: set[int]) -> set[int]:
        """
        Get the set of gov-ids based on a set of type-ids.
        """
        return self.gov.get_ids_by_types(type_ids)

    def get_names_by_ids(self, gov_ids: set[int]) -> set[str]:
        """
        Get the set of names based on a set of gov-ids.
        """
        return self.gov.get_names_by_ids(gov_ids)

    def get_ids_by_names(self, names: set[str]) -> set[int]:
        return self.gov.get_ids_by_names(names)

    def get_reachable_nodes_by_id(self, gov_ids: set[int]) -> set[int]:
        return self.gov.get_reachable_nodes_by_id(gov_ids)

