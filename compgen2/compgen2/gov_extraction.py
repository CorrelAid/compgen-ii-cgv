# -*- coding: utf-8 -*-
# #Complete GOV extract #10
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/10

import logging
from collections import defaultdict
from os import kill

## Imports
from pathlib import Path
from typing import DefaultDict

import numpy as np
import pandas as pd

from .const import *

logger = logging.getLogger(__name__)

def _set_retrieve(s: set):
    return next(iter(s))


class GOV:
    """Main class to work with GOV items.

    To work with this class you have to
        1. Initialize a new instance `Gov(data_root)`
        2. Load the data `gov.load_data()`
        3. Build the search indicies `gov.build_indices()`

    Then, you can start querying the data.

    Attributes:
        data_root (str): Path to a folder containing the data.
        fully_initialized (bool): Set to `True` if all data and indices are initialized.
        items (pd.DataFrame): content of govitems.csv
        names (pd.DataFrame): content of propertynames.csv
        types (pd.DataFrame): content of propertytypes.csv
        relations (pd.DataFrame): content of relation.csv
        type_names (pd.DataFrame): content of typenames.csv
        items_by_id_raw (dict): A mapping between an item's id and its textual id. Unfiltered raw data.
        types_by_id_raw (dict): A mapping between an item's id and its type. Unfiltered raw data.
        names_by_id_raw (dict): A mapping between an item's id and its names. Unfiltered raw data.
        items_by_id (dict): A mapping between an item's id and its textual id.
        types_by_id (dict): A mapping between an item's id and its type.
        names_by_id (dict): A mapping between an item's id and its names.
        ids_by_name (dict): A mapping between a name and its possible ids.
        all_relations (set): A set of all relations in GOV
        all_paths (set): A set of all paths in GOV from SUPERNODES to their children.
        all_reachable_nodes_by_id (dict): A mapping between an item's id and its reachable nodes.
    """

    def __init__(self, data_root: str) -> None:
        self.data_root = Path(data_root)
        self.fully_initialized = False

        # raw gov tables
        self.items = pd.DataFrame()
        self.names = pd.DataFrame()
        self.types = pd.DataFrame()
        self.relations = pd.DataFrame()
        self.type_names = pd.DataFrame()

        # important search indices
        self.items_by_id_raw = {}
        self.types_by_id_raw = {}
        self.names_by_id_raw = {}
        self.items_by_id = {}
        self.types_by_id = {}
        self.names_by_id = {}
        self.ids_by_name = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.years= {}


        logger.info("Initialized empty gov instance. Please call `load_data()` next.")

    def load_data(self):
        logger.info("Start loading all relevant GOV tables ...")
        self.items = self._read_item()
        self.names = self._read_names()
        self.types = self._read_types()
        self.relations = self._read_relations()
        self.type_names = self._read_type_names()

        # filter data
        self._prefilter_names()
        self._prefilter_relations()
        self._prefilter_types()

        logger.info(
            "Finished loading all relevant GOV tables. Please call `build_indices()` next."
        )

    def build_indices(self):
        """Build all relevant indices that are necessary for efficiently querying and working with GOV."""
        logger.info("Start building all relevant search indices ...")
        self.years = self.julian_years() 
        self.items_by_id_raw = self._items_by_id()
        self.names_by_id_raw = self._names_by_id()
        self.types_by_id_raw = self._types_by_id()
        self.all_relations = self._all_relations()
        self.all_paths = self._all_paths()
        self.ids_by_name = self._ids_by_name()
        self.all_reachable_nodes_by_id = self._all_reachable_nodes_by_id()
        self.fully_initialized = True

        logger.info(
            "Finished building all relevant search indices. You can now start working with GOV data."
        )

    def clear_data(self):
        """Necessary step to pickle model so that its size its manageable.

        If you unpickle a pipeline object you will have to call `load_data()` and `build_indices()` again.
        """
        self.items = pd.DataFrame()
        self.names = pd.DataFrame()
        self.types = pd.DataFrame()
        self.relations = pd.DataFrame()
        self.type_names = pd.DataFrame()
        self.items_by_id_raw = {}
        self.types_by_id_raw = {}
        self.names_by_id_raw = {}
        self.items_by_id = {}
        self.types_by_id = {}
        self.names_by_id = {}
        self.ids_by_name = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.fully_initialized = False
        self.years = {}

        logger.info("Cleared all data and attributes.")

    def _read_item(self) -> pd.DataFrame:
        """Read in govitems.csv"""
        logger.info("Reading in govitems.csv.")
        gov_item = pd.read_csv(
            self.data_root / GOV_ITEMS,
            sep="\t",
            dtype={"id": np.int32, "textual_id": object, "deleted": bool},
        )
        assert not gov_item.id.duplicated().any()
        return gov_item

    def _read_names(self) -> pd.DataFrame:
        """Read in propertynames.csv"""
        logger.info("Reading in propertynames.csv.")
        names = pd.read_csv(
            self.data_root / PROPERTY_NAMES,
            sep="\t",
            dtype={
                "id": np.int32,
                "content": object,
                "language": object,
                "time_begin": object,
                "time_end": object,
            },
        )
        names = GOV.convert_time(names)
        return names

    def _read_types(self) -> pd.DataFrame:
        """Read in propertytypes.csv"""
        logger.info("Reading in propertytypes.csv.")
        types = pd.read_csv(
            self.data_root / PROPERTY_TYPES,
            sep="\t",
            dtype={
                "id": np.int32,
                "content": np.int32,
                "time_begin": object,
                "time_end": object,
            },
        )
        types = GOV.convert_time(types)
        return types

    def _read_relations(self) -> pd.DataFrame:
        """Read in relation.csv"""
        logger.info("Reading in relation.csv.")
        relations = pd.read_csv(
            self.data_root / GOV_RELATIONS,
            sep="\t",
            dtype={
                "child": np.int32,
                "parent": np.int32,
                "time_begin": object,
                "time_end": object,
            },
        )
        relations = GOV.convert_time(relations)
        return relations

    def _read_type_names(self) -> pd.DataFrame:
        """Read in typenames.csv"""
        logger.info("Reading in typenames.csv.")
        type_names = pd.read_csv(
            self.data_root / GOV_TYPENAMES,
            sep="\t",
            index_col=0,
            dtype={
                "value": object,
            },
        )
        return type_names

    def _prefilter_names(self):
        """ Removes any data from the DataFrame that is tagged as deleted.
        """
        logger.info(f"Pre-filtering raw names.")
        logger.debug(f"Shape of names before filtering: {self.names.shape}")
        names_filtered = self.names.merge(
            self.items[["id", "deleted"]], left_on="id", right_on="id",
        )
        self.names = names_filtered.query("~deleted").drop(
            columns=["deleted"]
        )
        logger.debug(f"Shape of names after filtering: {self.names.shape}")

    def _prefilter_relations(self):
        """ Removes any data from the DataFrame that is tagged as deleted.
        """
        logger.info(f"Pre-filtering raw relations.")
        logger.debug(f"Shape of relations before filtering: {self.relations.shape}")
        # Filter relations DataFrame based on time
        relations_filtered = self.filter_time(self.relations)
        # Filter relations DataFrame based on deleted
        relations_filtered = relations_filtered.merge(
            self.items[["id", "deleted"]], left_on="child", right_on="id"
        )
        relations_filtered = relations_filtered.merge(
            self.items[["id", "deleted"]], left_on="parent", right_on="id"
        )
        self.relations = relations_filtered.query("~deleted_x and ~deleted_y").drop(
            columns=["id_x", "id_y", "deleted_x", "deleted_y"]
        )
        logger.debug(f"Shape of relations after filtering: {self.relations.shape}")

    def _prefilter_types(self):
        """ Removes any data from the DataFrame that is tagged as deleted.
        """
        logger.info(f"Pre-filtering raw types.")
        logger.debug(f"Shape of types before filtering: {self.types.shape}")
        types_filtered = self.types.merge(
            self.items[["id", "deleted"]], left_on="id", right_on="id",
        )
        self.types = types_filtered.query("~deleted").drop(
            columns=["deleted"]
        )
        logger.debug(f"Shape of types after filtering: {self.types.shape}")

    def _items_by_id(self) -> dict[int, tuple[str, bool]]:
        """Create a mapping from govitems with `id` as key and `textual_id` and `deleted` as values."""
        logger.info("Create items by id.")
        gov = set(
            zip(
                self.items.id,
                self.items.textual_id,
                self.items.deleted,
            )
        )
        gov_dict = {
            i[0]: (
                i[1],
                i[2],
            )
            for i in gov
        }
        return gov_dict

    def _names_by_id(self) -> dict[int, set[str]]:
        """Create a mapping from propertynames with `id` as key and `content` as value.

        All names associated with the same id are combined into a set.
        """
        logger.info("Create names by id.")
        names = set(
            zip(
                self.names.id,
                self.names.content,
                self.names.time_begin,
                self.names.time_end,
                self.names.language,
            )
        )

        name_dict = defaultdict(set)
        for n in names:
            name_dict[n[0]] |= {n[1:]}
        name_dict.default_factory = None
        return name_dict

    def _ids_by_name(self) -> dict[str, set[int]]:
        """Create a mapping from names to ids. Based on the filtered names.

        All ids associated with the same name are combined into a set.
        """
        logger.info("Create ids by name")

        ids_by_name = defaultdict(set)
        for k, v in self.names_by_id.items():
            for n in v:
                ids_by_name[n] |= {k}
        ids_by_name.default_factory = None
        return ids_by_name

    def _types_by_id(self) -> dict[int, set[int]]:
        """Create a mapping from propertytypes with `id` as key and `content` as value.

        All types associated with the same id are combined into a set.
        """
        logger.info("Create types by id.")
        types = set(
            zip(
                self.types.id,
                self.types.content,
                self.types.time_begin,
                self.types.time_end,
            )
        )
        type_dict = defaultdict(set)
        for t in types:
            type_dict[t[0]] |= {t[1:]}
        type_dict.default_factory = None
        return type_dict

    def _all_relations(self) -> set[tuple[int, int, str, str]]:
        """Transform the relations to set of tuples.
        """
        logger.info("Create all relations.")
        relations = set(
            zip(
                self.relations.parent,
                self.relations.child,
                self.relations.time_begin,
                self.relations.time_end,
            )
        )
        return relations

    def _all_paths(self) -> set[tuple[int, ...]]:
        """
        Return a set of paths, where each path is a set of all nodes from a SUPERNODE to a particular child.
        Additionally, collect all valid textual-ids, types, names of the resulting graph.
        """
        logger.info("Create all paths.")
        relations = self.all_relations
        leave_dict_curr = {k: {((k,), T_MIN, T_MAX)} for k in SUPERNODES}
        paths = set()
        new_leaves_found = True

        relevant_item_dict = dict()
        relevant_type_dict = defaultdict(set)
        relevant_name_dict = defaultdict(set)
        for k in SUPERNODES:
            self._collect_items(relevant_item_dict, k)
            self._collect_types(relevant_type_dict, k, T_BEGIN, T_END)
            self._collect_names(relevant_name_dict, k, T_BEGIN, T_END)

        while new_leaves_found:
            leave_dict_next = defaultdict(set)
            leaves_updated = set()
            for r in relations:
                if r[0] in leave_dict_curr:
                    for path in leave_dict_curr[r[0]]:
                        # Track the time-constrains of the path
                        tmin = max(r[2], path[1])
                        tmax = min(r[3], path[2])
                        if (r[2],r[3]) in self.years: # Special case: When the time-validity of the relation is exactly one year from January 1 to December 31, the constraint is meant as a lower limit only.
                            tmax = path[2]
                        if tmin > tmax:
                            continue
                        if self._collect_types(relevant_type_dict, r[1], tmin, tmax):
                            leaves_updated.add(r[0])
                            path_updated = ((*path[0], r[1]), tmin, tmax)
                            leave_dict_next[r[1]] |= {path_updated}
                            self._collect_items(relevant_item_dict, r[1])
                            self._collect_names(relevant_name_dict, r[1], tmin, tmax)
            for l in leaves_updated:
                del leave_dict_curr[l]
            # If no matching relation has been found for a path/leave, the path is final and can be moved to the final output.
            paths.update(*leave_dict_curr.values())
            if len(leaves_updated) == 0:
                new_leaves_found = False
            logger.debug(
                f"Final paths: {len(paths)}, Updated paths: {len(set().union(*leave_dict_next.values()))}"
            )
            leave_dict_curr = leave_dict_next
        relevant_type_dict.default_factory = None
        relevant_name_dict.default_factory = None
        self.items_by_id = relevant_item_dict
        self.types_by_id = relevant_type_dict
        self.names_by_id = relevant_name_dict
        paths = {p[0] for p in paths}  # Take path only. Without time_begin and time_end
        return paths

    def _collect_items(self, relevant_item_dict, k):
        """ 
        Extends the relevant_item_dict by the provided id k and its textual-id.
        """
        relevant_item_dict[k] = self.items_by_id_raw[k]

    def _collect_types(self, relevant_type_dict, k, tmin, tmax):
        """ 
        Extends the relevant_type_dict if the type and the time-constraints are valid.
        Returns:
            bool:
                If at least one type was added (all conditions have been met) the method returns True. Else the method returns False.
        """
        valid_type_found = False
        for t in self.types_by_id_raw[k]:
            if t[0] not in TUNDESIRED and ((t[1] <= tmax and t[2] >= tmin) or ((t[1],t[2]) in self.years and t[1] <= tmax)):
                relevant_type_dict[k] |= {t[0]}
                valid_type_found = True
        return valid_type_found

    def _collect_names(self, relevant_name_dict, k, tmin, tmax):
        """ 
        Extends the relevant_name_dict with at least one name.
        The method divides the name-candidates in six groups by priority.
        It picks the name(s) from the group with the highes priority. The other names are disregarded.
        * Group 1: Time constraint met + German
        * Group2 : Time constraint met + other more favorable languages
        * Group 3: Time constraint met + remaining langauges
        * Group 4: German (time constraint not met)
        * Group 5: other more favorable languages (time constraint not met)
        * Group 6: remaining languages (time constraint not met). If all prior groups were empty this will contain at least one name.
        """
        valid_names_prio1 = set()
        valid_names_prio2 = set()
        valid_names_prio3 = set()
        for n in self.names_by_id_raw[k]:
            if (n[1] <= tmax and n[2] >= tmin) or ((n[1],n[2]) in self.years and n[1] <= tmax):
                if n[3] == 'deu':
                    valid_names_prio1.add(n[0])
                elif n[3] in {'fre','pol', 'eng'}:
                    valid_names_prio2.add(n[0])
                else:
                    valid_names_prio3.add(n[0])
        if len(valid_names_prio1) > 0:
            # group 1
            relevant_name_dict[k] |= valid_names_prio1
        elif len(valid_names_prio1) > 0:
            # group 2
            relevant_name_dict[k] |= valid_names_prio2
        elif len(valid_names_prio3) > 0:
            # group 3
            relevant_name_dict[k] |= valid_names_prio3
        else:
            for n in self.names_by_id_raw[k]:
                if n[3] == 'deu':
                        valid_names_prio1.add(n[0])
                elif n[3] in {'fre','pol', 'eng'}:
                        valid_names_prio2.add(n[0])
                else:
                    valid_names_prio3.add(n[0])
            if len(valid_names_prio1) > 0:
                # group 4
                relevant_name_dict[k] |= valid_names_prio1
            elif len(valid_names_prio2) > 0:
                # group 5
                relevant_name_dict[k] |= valid_names_prio2
            else:
                # group 6
                relevant_name_dict[k] |= valid_names_prio3

    def _all_reachable_nodes_by_id(self) -> dict[int, set[int]]:
        """Find all reachable nodes for a given node."""
        logger.info("Create all reachable nodes by id.")
        reachable_nodes = defaultdict(set)

        for path in self.all_paths:
            for id_ in path:
                reachable_nodes[id_].update(set(path) - {id_})

        return reachable_nodes

    def decode_paths_id(self, paths: set) -> set:
        """Return the gov textual id for each node in a path."""
        paths_decoded = {tuple(self.items_by_id[o][0] for o in p) for p in paths}
        return paths_decoded

    def decode_paths_name(self, paths: set) -> set:
        """Return the gov display name for each node in a path."""
        paths_decoded = {
            tuple(_set_retrieve(self.names_by_id[o]) for o in p)
            for p in paths
        }
        return paths_decoded

    def extract_all_types_from_paths(self, paths: set) -> set:
        """Return all unique type ids over all paths."""
        types_relevant = set().union(*[self.types_by_id[n][0] for p in paths for n in p])
        return types_relevant

    def decode_paths_type(self, paths: set) -> set:
        """Return the type display name for each node in a path."""
        paths_decoded = {
            tuple(self.type_names.loc[_set_retrieve(self.types_by_id[o])][0] for o in p)
            for p in paths
        }
        return paths_decoded

    @staticmethod
    def convert_time(data: pd.DataFrame) -> pd.DataFrame:
        data = data.replace(
            {"time_begin": {np.NaN: T_MIN}, "time_end": {np.NaN: T_MAX}},
        ).astype(
            {
                "time_begin": np.int64,
                "time_end": np.int64,
            }
        )
        return data

    @staticmethod
    def filter_time(data: pd.DataFrame) -> pd.DataFrame:
        data = data.query(
            "time_begin < @T_BEGIN and time_end > @T_END"
        )  # TODO: Introduce correct time constraints for julian date???
        return data

    def julian_years(self) -> set[tuple[int,int]]:
        """ Compute the tuple (1st of January, 31st of December) in julian date format for all years from 1 A.D. to 3000 A.D.
        """
        new_years_day = 1721426 # 1721426 is 0001-01-01 12:00:00
        new_years_eve = 0
        years = set()
        for y in range(1,3001): # From year 1 A.D. to 3000 A.D.
            new_years_eve = new_years_day + 364 + int( y%4 == 0 and (y%100 !=0 or y%400 == 0) )
            years.add((new_years_day*10,new_years_eve*10))
            new_years_day = new_years_eve + 1
        return years