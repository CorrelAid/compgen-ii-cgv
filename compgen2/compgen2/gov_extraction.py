# -*- coding: utf-8 -*-
# #Complete GOV extract #10
# Issue link: https://github.com/CorrelAid/compgen-ii-cgv/issues/10

from collections import defaultdict
from functools import lru_cache
## Imports
from pathlib import Path

import numpy as np
import pandas as pd

from .const import *


class GOV:
    """Main class to work with GOV elements.

    Attributes:
        data_root (str):
        gov_items (pd.DataFrame):
        names (pd.DataFrame):
        types (pd.DataFrame):
        relations (pd.DataFrame):
        type_names (pd.DataFrame):

    """

    def __init__(self, data_root: str) -> None:
        self.data_root = Path(data_root)

        # load data
        self.gov_items = self.read_gov_item()
        self.names = self.read_names()
        self.types = self.read_types()
        self.relations = self.read_relations()
        self.type_names = self.read_type_names()

    def read_gov_item(self) -> pd.DataFrame:
        """Read in govitems.csv"""
        print("Reading in govitems.csv")
        gov_item = pd.read_csv(
            self.data_root / GOV_ITEMS,
            sep="\t",
            dtype={"id": np.int32, "textual_id": object, "deleted": bool},
        )
        assert not gov_item.id.duplicated().any()
        return gov_item

    def read_names(self) -> pd.DataFrame:
        """Read in propertynames.csv"""
        print("Reading in propertynames.csv")
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
        names = GOV.filter_names(names)
        names = GOV.filter_time(names)
        return names

    def read_types(self) -> pd.DataFrame:
        """Read in propertytypes.csv"""
        print("Reading in propertytypes.csv")
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
        types = GOV.filter_time(types)
        return types

    def read_relations(self) -> pd.DataFrame:
        """Read in relation.csv"""
        print("Reading in relation.csv")
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
        relations = GOV.filter_time(relations)
        return relations

    def read_type_names(self) -> pd.DataFrame:
        """Read in typenames.csv"""
        print("Reading in typenames.csv")
        type_names = pd.read_csv(
            self.data_root / GOV_TYPENAMES,
            sep="\t",
            index_col=0,
            dtype={
                "value": object,
            },
        )
        return type_names

    @lru_cache
    def build_gov_dict(self) -> dict[int, tuple[str, bool]]:
        """Create a mapping from govitems with `id` as key and `textual_id` and `deleted` as values."""
        gov = set(
            zip(
                self.gov_items.id,
                self.gov_items.textual_id,
                self.gov_items.deleted,
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

    @lru_cache
    def build_name_dict(self) -> dict[int, set[str]]:
        """Create a mapping from propertynames with `id` as key and `content` as value.

        All names associated with the same id are combined into a set.
        """
        names = set(
            zip(
                self.names.id,
                self.names.content,
            )
        )
        name_dict = defaultdict(set)
        for n in names:
            name_dict[n[0]] |= {n[1]}
        return name_dict

    @lru_cache
    def build_type_dict(self) -> dict[int, set[int]]:
        """Create a mapping from propertytypes with `id` as key and `content` as value.

        All names associated with the same id are combined into a set.
        """
        types = set(
            zip(
                self.types.id,
                self.types.content,
            )
        )
        type_dict = defaultdict(set)
        for t in types:
            type_dict[t[0]] |= {t[1]}
        return type_dict

    @lru_cache
    def filter_relations(self) -> set[tuple[int, int, str, str]]:
        """Find all relations that are children of the SUPERNODES defined.

        Transform the relations to tuples.
        Ignore all relations with undesired types.
        """
        relations_unfiltered = set(
            zip(
                self.relations.parent,
                self.relations.child,
                self.relations.time_begin,
                self.relations.time_end,
            )
        )
        relations_unfiltered = self.filter_relation(relations_unfiltered)
        relations_filtered = set()

        # begin with SUPERNODES, find all children and their children
        leaves_current = SUPERNODES
        new_leaves_found = True

        gov_dict = self.build_gov_dict()

        while new_leaves_found:
            leaves_next = set()
            for r in relations_unfiltered:
                # only consider relation when parent is in current leaves and child has deleted = 0
                if r[0] in leaves_current and gov_dict[r[1]][1] == 0:
                    relations_filtered.add(r)
                    leaves_next.add(r[1])
            relations_unfiltered.difference_update(relations_filtered)
            if len(leaves_next) == 0:
                new_leaves_found = False

            print(
                f"old: {len(relations_unfiltered)}, new: {len(relations_filtered)}, sample-child: {tuple(leaves_next)[:1]}"
            )
            leaves_current = leaves_next

        return relations_filtered

    @lru_cache
    def build_paths(self) -> set[tuple[int, ...]]:
        """Return a set of paths, where each path is a set of all nodes from a SUPERNODE to a particular child."""
        relations = self.filter_relations()
        leave_dict_curr = {k: {((k,), T_MIN, T_MAX)} for k in SUPERNODES}
        paths = set()
        new_leaves_found = True

        while new_leaves_found:
            leave_dict_next = dict()
            leaves_updated = set()
            for r in relations:
                if r[0] in leave_dict_curr:
                    for path in leave_dict_curr[r[0]]:
                        tmin = min(r[2], path[1])
                        tmax = max(r[3], path[2])
                        if tmin <= tmax:  # TODO: Introduce correct time constraints???
                            leaves_updated.add(r[0])
                            path_updated = ((*path[0], r[1]), tmin, tmax)
                            leave_dict_next[r[1]] = {path_updated}.union(
                                leave_dict_next.setdefault(r[1], set())
                            )
            for l in leaves_updated:
                del leave_dict_curr[l]
            paths.update(*leave_dict_curr.values())
            if len(leaves_updated) == 0:
                new_leaves_found = False

            print(
                f"Final paths: {len(paths)}, Updated paths: {len(set().union(*leave_dict_next.values()))}"
            )
            leave_dict_curr = leave_dict_next

        paths = {p[0] for p in paths}  # take path only without time_begin and time_end
        return paths

    def decode_paths_id(self, paths: set) -> set:
        gov_dict = self.build_gov_dict()
        paths_decoded = {tuple(gov_dict[o][0] for o in p) for p in paths}
        return paths_decoded

    def decode_paths_name(self, paths: set) -> set:
        name_dict = self.build_name_dict()
        paths_decoded = {tuple(name_dict[o].pop() for o in p) for p in paths}
        return paths_decoded

    def filter_relation(self, relations: set) -> set:
        type_dict = self.build_type_dict()
        relations_filtered = {
            r for r in relations if not (type_dict[r[0]] | type_dict[r[1]]) & TUNDESIRED
        }
        return relations_filtered

    def extract_all_types_from_paths(self, paths: set) -> set:
        type_dict = self.build_type_dict()
        types_relevant = set().union(*[type_dict[n] for p in paths for n in p])
        return types_relevant

    def decode_paths_type(self, paths: set) -> set:
        type_dict = self.build_type_dict()
        type_names = self.read_type_names()
        paths_decoded = {
            tuple(type_names.loc[type_dict[o].pop()][0] for o in p) for p in paths
        }
        return paths_decoded

    @staticmethod
    def filter_time(data: pd.DataFrame) -> pd.DataFrame:
        data = data.replace(
            {"time_begin": {np.NaN: T_MIN}, "time_end": {np.NaN: T_MAX}},
        ).astype(
            {
                "time_begin": np.int64,
                "time_end": np.int64,
            }
        )
        data = data.query(
            "time_begin < @T_BEGIN and time_end > @T_END"
        )  # TODO: Introduce correct time constraints for julian date???
        return data

    @staticmethod
    def filter_names(names: pd.DataFrame) -> pd.DataFrame:
        names = names.query("language == 'deu'")
        return names
