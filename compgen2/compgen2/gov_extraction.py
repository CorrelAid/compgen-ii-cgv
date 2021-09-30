# -*- coding: utf-8 -*-
# #Complete GOV extract #10
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/10

import logging
from collections import defaultdict

## Imports
from pathlib import Path

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
        items_by_id (dict): A mapping between an item's id and its textual id.
        names_by_id (dict): A mapping between an item's id and its names.
        ids_by_name (dict): A mapping between a name and its possible ids.
        types_by_id (dict): A mapping between an item's id and its type.
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
        self.items_by_id = {}
        self.names_by_id = {}
        self.ids_by_name = {}
        self.types_by_id = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.julian_by_year= {}

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
        self.julian_by_year = self._julian_years()
        self.items_by_id = self._items_by_id()
        self.names_by_id = self._names_by_id()
        self.ids_by_name = self._ids_by_name()
        self.types_by_id = self._types_by_id()
        self.all_relations = self._all_relations()
        self.all_paths = self._all_paths()
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
        self.items_by_id = {}
        self.names_by_id = {}
        self.ids_by_name = {}
        self.types_by_id = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.fully_initialized = False
        self.julian_by_year = {}

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
        self.names = self.names.query("language == 'deu'").drop(columns="language")

    def _prefilter_relations(self):
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

    def _prefilter_types(self):
        # The GOV does not store types for deleted objects. Hence no filtering by deleted necessary here.
        pass

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
            )
        )

        name_dict = defaultdict(set)
        for n in names:
            name_dict[n[0]] |= {n[1]}
        name_dict.default_factory = None
        return name_dict

    def _ids_by_name(self) -> dict[str, set[int]]:
        """Create a mapping from propertynames with `content` as key and `id` as value.

        All ids associated with the same name are combined into a set.
        """
        logger.info("Create ids by name")
        return self.names.groupby("content").id.apply(set).to_dict()

    def _types_by_id(self) -> dict[int, set[int]]:
        """Create a mapping from propertytypes with `id` as key and `content` as value.

        All types associated with the same id are combined into a set.
        """
        logger.info("Create types by id.")
        types = set(
            zip(
                self.types.id,
                self.types.content,
            )
        )
        type_dict = defaultdict(set)
        for t in types:
            type_dict[t[0]] |= {t[1]}
        type_dict.default_factory = None
        return type_dict

    def _all_relations(self) -> set[tuple[int, int, str, str]]:
        """Transform the relations to set of tuples.
        Filter by specific criteria
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
        relations = self.filter_relations_by_type(relations)
        relations = self.filter_relations_by_ancestor(relations)
        return relations

    def filter_relations_by_type(
        self, relations: set[tuple[int, int, str, str]]
    ) -> set[tuple[int, int, str, str]]:
        """Filter relations that contain objects with undesired types."""
        type_dict = self.types_by_id
        relations_filtered = {
            r for r in relations if not (type_dict[r[0]] | type_dict[r[1]]) & TUNDESIRED
        }
        return relations_filtered

    def filter_relations_by_ancestor(
        self, relations_unfiltered: set[tuple[int, int, str, str]]
    ) -> set[tuple[int, int, str, str]]:
        """Find all relations that are children of the SUPERNODES defined."""

        # begin with SUPERNODES, find all children and their children
        leaves_current = SUPERNODES
        new_leaves_found = True
        relations_filtered = set()

        while new_leaves_found:
            leaves_next = set()
            for r in relations_unfiltered:
                # only consider relation when parent is in current leaves and child has deleted = 0
                if r[0] in leaves_current:
                    relations_filtered.add(r)
                    leaves_next.add(r[1])
            relations_unfiltered.difference_update(relations_filtered)
            if len(leaves_next) == 0:
                new_leaves_found = False

            logger.debug(
                f"old: {len(relations_unfiltered)}, new: {len(relations_filtered)}, sample-child: {tuple(leaves_next)[:1]}"
            )
            leaves_current = leaves_next

        return relations_filtered

    def _all_paths(self) -> set[tuple[int, ...]]:
        """Return a set of paths, where each path is a set of all nodes from a SUPERNODE to a particular child."""
        logger.info("Create all paths.")
        relations = self.all_relations
        leave_dict_curr = {k: {((k,), T_MIN, T_MAX)} for k in SUPERNODES}
        paths = set()
        new_leaves_found = True

        while new_leaves_found:
            leave_dict_next = defaultdict(set)
            leaves_updated = set()
            for r in relations:
                if r[0] in leave_dict_curr:
                    for path in leave_dict_curr[r[0]]:
                        tmin = max(r[2], path[1])
                        tmax = min(r[3], path[2])
                        if r[2]//10 < T_BEGIN and (r[2]//10,r[3]//10) in self.julian_by_year.values():
                            tmax = path[2]
                        if tmin <= tmax:  # TODO: Introduce correct time constraints???
                            leaves_updated.add(r[0])
                            path_updated = ((*path[0], r[1]), tmin, tmax)
                            leave_dict_next[r[1]] |= {path_updated}
            # If no matching relation has been found for a path/leave, the path is final and can be moved to the final output.
            for l in leaves_updated:
                del leave_dict_curr[l]
            paths.update(*leave_dict_curr.values())
            if len(leaves_updated) == 0:
                new_leaves_found = False

            logger.debug(
                f"Final paths: {len(paths)}, Updated paths: {len(set().union(*leave_dict_next.values()))}"
            )
            leave_dict_curr = leave_dict_next

        paths = {p[0] for p in paths}  # take path only without time_begin and time_end
        return paths

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
        gov_dict = self.items_by_id
        paths_decoded = {tuple(gov_dict[o][0] for o in p) for p in paths}
        return paths_decoded

    def decode_paths_name(self, paths: set) -> set:
        """Return the gov display name for each node in a path."""
        name_dict = self.names_by_id
        paths_decoded = {
            tuple(_set_retrieve(name_dict.get(o, set("<error>"))) for o in p)
            for p in paths
        }
        return paths_decoded

    def extract_all_types_from_paths(self, paths: set) -> set:
        """Return all unique type ids over all paths."""
        type_dict = self.types_by_id
        types_relevant = set().union(*[type_dict[n] for p in paths for n in p])
        return types_relevant

    def decode_paths_type(self, paths: set) -> set:
        """Return the type display name for each node in a path."""
        type_dict = self.types_by_id
        paths_decoded = {
            tuple(self.type_names.loc[_set_retrieve(type_dict[o])][0] for o in p)
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

    def _julian_years(self) -> dict[int, tuple[int,int]]:
        """ Compute the tuple (1st of January, 31st of December) in julian date format for all years from 1 A.D. to 3000 A.D.
        """
        new_years_day = 1721426 # 1721426 is 0001-01-01 12:00:00
        new_years_eve = 0
        julian_by_year = dict()
        for y in range(1,3001):
            new_years_eve = new_years_day + 364 + int( y%4 == 0 and (y%100 !=0 or y%400 == 0) )
            julian_by_year[y] = (new_years_day,new_years_eve)
            new_years_day = new_years_eve + 1
        return julian_by_year