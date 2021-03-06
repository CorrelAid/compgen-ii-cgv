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

from ..const import *

logger = logging.getLogger(__name__)


def _set_retrieve(s: set):
    return next(iter(s))


class Gov:
    """Main class to work with Gov items.

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
        types_by_id (dict): A mapping between an item's id and its type.
        names_by_id (dict): A mapping between an item's id and its names.
        ids_by_name (dict): A mapping between a name and its possible ids.
        type_names_by_type (dict): A mapping from the type-id to its type-name.
        all_relations (set): A set of all relations in Gov
        all_paths (set): A set of all paths in Gov from SUPERNODES to their children.
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
        self._items_by_id_raw = {}
        self._types_by_id_raw = {}
        self._names_by_id_raw = {}
        self.items_by_id = {}
        self.types_by_id = defaultdict(set)
        self.names_by_id = defaultdict(set)
        self.ids_by_name = {}
        self.ids_by_type = {}
        self.type_names_by_type = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.years = {}

        logger.info("Initialized empty gov instance. Please call `load_data()` next.")

    @staticmethod
    def from_file(file: str):
        """Load serialized Gov object."""
        with open(file, "rb") as stream:
            gov = pickle.load(stream)
        return gov

    def load_data(self):
        if self.fully_initialized:
            return

        logger.info("Start loading all relevant Gov tables ...")
        self.items = self._read_item()
        self.names = self._read_names()
        self.types = self._read_types()
        self.relations = self._read_relations()
        self.type_names = self._read_type_names()

        # filter data
        self._prefilter_names()
        self._prefilter_relations()
        self._prefilter_types()

        logger.info("Finished loading all relevant Gov tables. Please call `build_indices()` next.")

    def build_indices(self):
        """Build all relevant indices that are necessary for efficiently querying and working with Gov."""
        if self.fully_initialized:
            return

        logger.info("Start building all relevant search indices ...")
        self.years = self.julian_years()
        self._items_by_id_raw = self._items_by_id()
        self._names_by_id_raw = self._names_by_id()
        self._types_by_id_raw = self._types_by_id()
        self.type_names_by_type = self._type_names_by_type()
        self.all_relations = self._all_relations()
        self.all_paths = self._all_paths()
        self.ids_by_type = self._ids_by_type()
        self.ids_by_name = self._ids_by_name()
        self.all_reachable_nodes_by_id = self._all_reachable_nodes_by_id()
        self.fully_initialized = True

        logger.info("Finished building all relevant search indices. You can now start working with Gov data.")

    def clear_data(self):
        """Necessary step to pickle model so that its size its manageable.

        If you unpickle a pipeline object you will have to call `load_data()` and `build_indices()` again.
        """
        self.items = pd.DataFrame()
        self.names = pd.DataFrame()
        self.types = pd.DataFrame()
        self.relations = pd.DataFrame()
        self.type_names = pd.DataFrame()
        self._items_by_id_raw = {}
        self._types_by_id_raw = {}
        self._names_by_id_raw = {}
        self.items_by_id = {}
        self.types_by_id = defaultdict(set)
        self.names_by_id = defaultdict(set)
        self.ids_by_type = {}
        self.ids_by_name = {}
        self.type_names_by_type = {}
        self.all_relations = set()
        self.all_paths = set()
        self.all_reachable_nodes_by_id = {}
        self.years = {}

        self.fully_initialized = False

        logger.info("Cleared all data and attributes.")
        
    def get_loc_names(self) -> set[str]:
        """Return all location names stored in Gov

        Returns:
            set[str]: set of names
        """
        loc_names = set(self.ids_by_name.keys())
        return loc_names

    def _read_item(self) -> pd.DataFrame:
        """Read in govitems.csv"""
        logger.info("Reading in govitems.csv.")
        gov_item = pd.read_csv(
            self.data_root / FILENAME_GOV_ITEMS,
            sep="\t",
            dtype={"id": np.int32, "textual_id": object, "deleted": bool},
        )
        assert not gov_item.id.duplicated().any()
        return gov_item

    def _read_names(self) -> pd.DataFrame:
        """Read in propertynames.csv"""
        logger.info("Reading in propertynames.csv.")
        names = pd.read_csv(
            self.data_root / FILENAME_GOV_PROPERTY_NAMES,
            sep="\t",
            dtype={
                "id": np.int32,
                "content": object,
                "language": object,
                "time_begin": object,
                "time_end": object,
            },
        )
        names = Gov.convert_time(names)
        return names

    def _read_types(self) -> pd.DataFrame:
        """Read in propertytypes.csv"""
        logger.info("Reading in propertytypes.csv.")
        types = pd.read_csv(
            self.data_root / FILENAME_GOV_PROPERTY_TYPES,
            sep="\t",
            dtype={
                "id": np.int32,
                "content": np.int32,
                "time_begin": object,
                "time_end": object,
            },
        )
        types = Gov.convert_time(types)
        return types

    def _read_relations(self) -> pd.DataFrame:
        """Read in relation.csv"""
        logger.info("Reading in relation.csv.")
        relations = pd.read_csv(
            self.data_root / FILENAME_GOV_RELATIONS,
            sep="\t",
            dtype={
                "child": np.int32,
                "parent": np.int32,
                "time_begin": object,
                "time_end": object,
            },
        )
        relations = Gov.convert_time(relations)
        return relations

    def _read_type_names(self) -> pd.DataFrame:
        """Read in typenames.csv"""
        logger.info("Reading in typenames.csv.")
        type_names = pd.read_csv(
            self.data_root / FILENAME_GOV_TYPENAMES,
            sep="\t",
            dtype={
                "type_id": int,
                "language": object,
                "value": object,
            },
        )
        return type_names

    def _prefilter_names(self):
        """Removes any data from the DataFrame that is tagged as deleted."""
        logger.info(f"Pre-filtering raw names.")
        logger.debug(f"Shape of names before filtering: {self.names.shape}")
        names_filtered = self.names.merge(
            self.items[["id", "deleted"]],
            left_on="id",
            right_on="id",
        )
        self.names = names_filtered.query("~deleted").drop(columns=["deleted"])
        logger.debug(f"Shape of names after filtering: {self.names.shape}")

    def _prefilter_relations(self):
        """Removes any data from the DataFrame that is tagged as deleted."""
        logger.info(f"Pre-filtering raw relations.")
        logger.debug(f"Shape of relations before filtering: {self.relations.shape}")
        # Filter relations DataFrame based on time
        relations_filtered = self.filter_time(self.relations)
        # Filter relations DataFrame based on deleted
        relations_filtered = relations_filtered.merge(self.items[["id", "deleted"]], left_on="child", right_on="id")
        relations_filtered = relations_filtered.merge(self.items[["id", "deleted"]], left_on="parent", right_on="id")
        self.relations = relations_filtered.query("~deleted_x and ~deleted_y").drop(
            columns=["id_x", "id_y", "deleted_x", "deleted_y"]
        )
        logger.debug(f"Shape of relations after filtering: {self.relations.shape}")

    def _prefilter_types(self):
        """Removes any data from the DataFrame that is tagged as deleted."""
        logger.info(f"Pre-filtering raw types.")
        logger.debug(f"Shape of types before filtering: {self.types.shape}")
        types_filtered = self.types.merge(
            self.items[["id", "deleted"]],
            left_on="id",
            right_on="id",
        )
        self.types = types_filtered.query("~deleted").drop(columns=["deleted"])
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
                self.names.content.str.lower(),
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

    def _ids_by_type(self) -> dict[int, set[int]]:
        """Create a mapping from types to ids. Based on the filtered types.

        All ids associated with the same type are combined into a set.
        """
        logger.info("Create ids by type.")

        ids_by_type = defaultdict(set)
        for k, v in self.types_by_id.items():
            for t in v:
                ids_by_type[t] |= {k}
        ids_by_type.default_factory = None
        return ids_by_type

    def _type_names_by_type(self) -> dict[int, str]:
        """Create a mapping from the type-id to its type-name."""
        logger.info("Create type_names by type.")
        typenames = set(
            zip(
                self.type_names.type_id,
                self.type_names.language,
                self.type_names.value,
            )
        )
        type_names_dict = dict()
        for t in typenames:
            if t[1] == "deu":
                type_names_dict[t[0]] = t[2]
        return type_names_dict

    def _all_relations(self) -> set[tuple[int, int, str, str]]:
        """Transform the relations to set of tuples."""
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
        paths_by_leaf_curr = {k: {((k,), T_BEGIN, T_END)} for k in SUPERNODES}
        paths = set()
        new_leaves_found = True

        self.items_by_id = dict()
        self.types_by_id = defaultdict(set)
        self.names_by_id = defaultdict(set)
        for k in SUPERNODES:
            self._collect_item(self.items_by_id, k)
            self._collect_type(self.types_by_id, k, T_BEGIN, T_END)
            self._collect_name(self.names_by_id, k, T_BEGIN, T_END)

        while new_leaves_found:
            paths_by_leaf_next = defaultdict(set)
            leaves_updated = set()
            for r in relations:
                if r[0] in paths_by_leaf_curr:
                    for path in paths_by_leaf_curr[r[0]]:
                        # Track the time-constrains of the path
                        tmin = max(r[2], path[1])
                        tmax = min(r[3], path[2])
                        if (
                            r[2],
                            r[3],
                        ) in self.years:  # Special case: When the time-validity of the relation is exactly one year from January 1 to December 31, the constraint is meant as a lower limit only.
                            tmax = path[2]
                        if tmin > tmax:
                            continue
                        if self._collect_type(self.types_by_id, r[1], tmin, tmax):
                            leaves_updated.add(r[0])
                            path_updated = ((*path[0], r[1]), tmin, tmax)
                            paths_by_leaf_next[r[1]] |= {path_updated}
                            self._collect_item(self.items_by_id, r[1])
                            self._collect_name(self.names_by_id, r[1], tmin, tmax)
            for l in leaves_updated:
                del paths_by_leaf_curr[l]
            # If no matching relation has been found for a path/leave, the path is final and can be moved to the final output.
            paths.update(*paths_by_leaf_curr.values())
            if len(leaves_updated) == 0:
                new_leaves_found = False
            logger.debug(f"Final paths: {len(paths)}, Updated paths: {len(set().union(*paths_by_leaf_next.values()))}")
            paths_by_leaf_curr = paths_by_leaf_next
        self.types_by_id.default_factory = None
        self.names_by_id.default_factory = None
        paths = {p[0] for p in paths}  # Take path only. Without time_begin and time_end
        return paths

    def _collect_item(self, item_dict: dict(), k: int):
        """
        Extends the item_dict by the provided id k and its textual-id.
        """
        item_dict[k] = self._items_by_id_raw[k][0]

    def _collect_type(self, type_dict: defaultdict(set), k: int, tmin: int, tmax: int):
        """
        Extends the type_dict if the type and the time-constraints are valid.
        Returns:
            bool:
                If at least one type was added (all conditions have been met) the method returns True. Else the method returns False.
        """
        valid_type_found = False
        for t in self._types_by_id_raw[k]:
            if t[0] not in T_UNDESIRED and (
                (t[1] <= tmax and t[2] >= tmin) or ((t[1], t[2]) in self.years and t[1] <= tmax)
            ):
                type_dict[k] |= {t[0]}
                valid_type_found = True
        return valid_type_found

    def _collect_name(self, name_dict: defaultdict(set), k: int, tmin: int, tmax: int):
        """
        Extends the name_dict with at least one name.
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
        for n in self._names_by_id_raw[k]:
            if (n[1] <= tmax and n[2] >= tmin) or ((n[1], n[2]) in self.years and n[1] <= tmax):
                if n[3] == "deu":
                    valid_names_prio1.add(n[0])
                elif n[3] in {"fre", "pol", "eng"}:
                    valid_names_prio2.add(n[0])
                else:
                    valid_names_prio3.add(n[0])
        if len(valid_names_prio1) > 0:
            # group 1
            name_dict[k] |= valid_names_prio1
        elif len(valid_names_prio1) > 0:
            # group 2
            name_dict[k] |= valid_names_prio2
        elif len(valid_names_prio3) > 0:
            # group 3
            name_dict[k] |= valid_names_prio3
        else:
            for n in self._names_by_id_raw[k]:
                if n[3] == "deu":
                    valid_names_prio1.add(n[0])
                elif n[3] in {"fre", "pol", "eng"}:
                    valid_names_prio2.add(n[0])
                else:
                    valid_names_prio3.add(n[0])
            if len(valid_names_prio1) > 0:
                # group 4
                name_dict[k] |= valid_names_prio1
            elif len(valid_names_prio2) > 0:
                # group 5
                name_dict[k] |= valid_names_prio2
            else:
                # group 6
                name_dict[k] |= valid_names_prio3

    def _all_reachable_nodes_by_id(self) -> dict[int, set[int]]:
        """Find all reachable nodes for a given node."""
        logger.info("Create all reachable nodes by id.")
        reachable_nodes = defaultdict(set)

        for path in self.all_paths:
            for id_ in path:
                reachable_nodes[id_].update(set(path) - {id_})

        return reachable_nodes

    def decode_path_id(self, path: tuple[int]) -> tuple[int]:
        """Return the gov textual id for each node in a path."""
        path_decoded = tuple(self.items_by_id[o] for o in path)
        return path_decoded

    def decode_path_name(self, path: tuple[int]) -> tuple[str]:
        """Return the gov display name for each node in a path."""
        path_decoded = tuple(_set_retrieve(self.names_by_id[o]) for o in path)
        return path_decoded

    def decode_path_type(self, path: tuple[int]) -> tuple[int]:
        """Return the type display name for each node in a path."""
        path_decoded = tuple(self.type_names_by_type[_set_retrieve(self.types_by_id[o])] for o in path)
        return path_decoded

    def get_ids_by_types(self, type_ids: set[int]) -> set[int]:
        """
        Get the set of gov-ids based on a set of type-ids.
        """
        gov_ids = set().union(*(self.ids_by_type.get(t, set()) for t in type_ids))
        return gov_ids

    def get_names_by_ids(self, gov_ids: set[int]) -> set[str]:
        """
        Get the set of names based on a set of gov-ids.
        """
        names = set().union(*(self.names_by_id.get(i, set()) for i in gov_ids))
        return names

    def get_ids_by_names(self, names: set[str]) -> set[int]:
        ids = set().union(*(self.ids_by_name.get(name, set()) for name in names))
        return ids

    def get_reachable_nodes_by_id(self, gov_ids: set[int]) -> set[int]:
        ids = set().union(*(self.all_reachable_nodes_by_id.get(id_, set()) for id_ in gov_ids))
        return ids

    @staticmethod
    def convert_time(data: pd.DataFrame) -> pd.DataFrame:
        data = data.replace({"time_begin": {np.NaN: T_MIN}, "time_end": {np.NaN: T_MAX}},).astype(
            {
                "time_begin": np.int64,
                "time_end": np.int64,
            }
        )
        return data

    @staticmethod
    def filter_time(data: pd.DataFrame) -> pd.DataFrame:
        data = data.query(
            "time_begin < @T_END and time_end > @T_BEGIN"
        )  # TODO: Introduce correct time constraints for julian date???
        return data

    def julian_years(self) -> set[tuple[int, int]]:
        """Compute the tuple (1st of January, 31st of December) in julian date format for all years from 1 A.D. to 3000 A.D."""
        new_years_day = 1721426  # 1721426 is 0001-01-01 12:00:00
        new_years_eve = 0
        years = set()
        for y in range(1, 3001):  # From year 1 A.D. to 3000 A.D.
            new_years_eve = new_years_day + 364 + int(y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))
            years.add((new_years_day * 10, new_years_eve * 10))
            new_years_day = new_years_eve + 1
        return years

    def type_statistic(self, type_subset: set = set(), markdown_style_output=False, return_dict=False) -> list[tuple]:
        """
        Print the statistic of all types in the gov class
        Args:
            type_subset (set): Limit the statistic to a specific subset of types (optional)
            markdown_style_output (bool): If True, the method will print the output such that it can be used as a markdown table
            return_dict (bool): If True, the count_by_type dictionary is returned
        """
        from operator import itemgetter

        all_type_values = self.types_by_id.values()
        count_by_type = {}
        for types in self.types_by_id.values():
            for t in types:
                if t in type_subset or len(type_subset) == 0:
                    count_by_type[t] = count_by_type.get(t, 0) + 1
        count_by_type = dict(
            (k, (v, f"{v/len(all_type_values):.6f}", self.type_names_by_type[k])) for k, v in count_by_type.items()
        )
        for o in sorted(count_by_type.items(), key=itemgetter(1), reverse=True):
            if markdown_style_output:
                print(
                    f"|[{o[0]}](http://wiki-de.genealogy.net/Gov/Objekttyp_{o[0]}) | {o[1][0]} | {o[1][1]} | {o[1][2]}|"
                )
            else:
                print(o)
        if return_dict:
            return count_by_type
