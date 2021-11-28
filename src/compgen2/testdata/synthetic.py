import random
from collections import defaultdict

import pandas as pd

from .. import Gov, const_synthetic
from . import Manipulator, StringEnriched

# import compgen2.string_utils.linguistic
# import compgen2.string_utils.manipulator

random.seed(1337)


class Synthetic:
    def __init__(self, gov: Gov) -> None:
        self.gov = gov
        self.test_set = pd.DataFrame()
        self.fractal_dict = self._fractal_dict()
        self.lino_dict = self._linotype_dict()
        self.m_linotype = Manipulator(self.linotype, "char", const_synthetic.P_LINO)
        self.m_fractal = Manipulator(self.fractal, "char", const_synthetic.P_FRACTAL)
        self.m_drop = Manipulator(self.drop, "char", const_synthetic.P_DROP)
        self.m_shorten = Manipulator(self.shorten, "word", const_synthetic.P_SHORTEN)
        self.MANIPULATION_STEPS = [self.m_linotype, self.m_fractal, self.m_drop, self.m_shorten]

    def create_synthetic_test_set(self, size: int, num_parts:int = 2, distortion_factor = 1.) -> pd.DataFrame:
        """
        Create a synthetic dataset based on the paths of the Gov object that has been loaded priorly.
        Args:
          size (int): number of synthetic records that get created
        """
        all_paths = list(self.gov.all_paths)
        test_set = {"location": [], "truth": []}
        while len(test_set["location"]) < size:
            p_id = random.choice(all_paths)
            if len(p_id) < num_parts:
                continue
            p = self.gov.decode_path_name(p_id)
            location = self.create_location_from_path(p, num_parts)
            location_string = ", ".join(location)
            if location_string in test_set["truth"]:
                continue
            test_set["truth"].append(location_string)
            
            location = self.shuffle_order(location)
            se = StringEnriched(", ".join(location))
            for m in self.MANIPULATION_STEPS:
                se.apply_manipulator(m, distortion_factor)
            test_set["location"].append(se.get_string())

        self.test_set = pd.DataFrame(test_set)
        return self.test_set
    def _linotype_dict(self) -> dict[str, set[str]]:
        """
        Create a mapping from a character to all its neighboured characters on the linotype keyboard
        """
        lino_dict = defaultdict(set)
        rows = len(const_synthetic.key_matrix_linotype_reduced)
        cols = len(const_synthetic.key_matrix_linotype_reduced[0])
        for i in range(rows):
            for j in range(cols):
                c = const_synthetic.key_matrix_linotype_reduced[i][j]
                if i > 0:
                    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i - 1][j]}
                if j > 0:
                    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i][j - 1]}
                if j < cols - 1:
                    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i][j + 1]}
                if i < rows - 1:
                    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i + 1][j]}
                lino_dict[c].difference_update({"@"})
                digits = {str(n) for n in range(10)}
                if c in digits:
                    lino_dict[c].intersection_update(digits)
                else:
                    lino_dict[c].difference_update(digits)
        del lino_dict["@"]
        lino_dict.default_factory = None
        return lino_dict

    def _fractal_dict(self) -> dict[str, set[str]]:
        """
        Create a mapping from a letter to all letters that are visually similar in fractal font
        """
        fractal_dict = defaultdict(set)
        for p in const_synthetic.fractal_confusion_pairs:
            fractal_dict[p[0]] |= {p[1]}
            fractal_dict[p[1]] |= {p[0]}
        fractal_dict.default_factory = None
        return fractal_dict

    def create_location_from_path(self, p: tuple, num_parts: int = 2) -> list:
        """
        Picks two objects from a tuple (one in case of len(p)==1)
        Args:
          p: tuple
        Returns
          locations: list
        """
        return random.sample(p, k=num_parts)

    def shuffle_order(self, l: list) -> list:
        """
        Shuffle a list of objects with a given probability P_SHUFFLE
        Args:
          l: list
        """
        if random.random() < const_synthetic.P_SHUFFLE:
            return l[::-1]
        else:
            return l

    def shorten(self, w: str) -> str:
        """
        Word-based.
        Drop the last n characters of a word where n is randomly chosen. Insert a period after the remaining characters.
        """
        if len(w) > 1:
            c = random.randint(1, len(w) - 1)
            return w[0:c] + "."
        else:
            return w
        # if r+1 == len(l) or l[r+1] != ".":
        #    l.insert(r+1,".")

    def linotype(self, c: str) -> str:
        """
        Character-based.
        """
        return random.choice(list(self.lino_dict.get(c, {c})))  ## choose a random neighboured key

    def fractal(self, c: str) -> str:
        """
        Character-based.
        """
        return random.choice(list(self.fractal_dict.get(c, {c})))  ## choose a random similar letter

    def drop(self, _: str) -> str:
        """
        Character-based.
        """
        return ""


def sample_test_set_from_gov(gov: Gov, size: int, num_parts: int = 2, valid: float = 1) -> pd.DataFrame:
    test_set = {"location": [], "truth": []}
    population = list(gov.names_by_id)

    while len(test_set["location"]) != size:
        sample_id = random.sample(population=population, k=1)[0]
        while True:
            sample_nodes = random.sample(gov.all_reachable_nodes_by_id[sample_id], k=num_parts)
            try:
                item = ", ".join(
                        map(
                            lambda id_: random.sample(list(gov.names_by_id[id_]), k=1)[0],
                            sample_nodes,
                        )
                    )
                if item in test_set["location"]:
                    break
                
                test_set["location"].append(item)
                test_set["truth"].append(item)
                break
            except KeyError:
                pass
            
    test_set = pd.DataFrame(test_set)

    if valid < 1:
        num_invalid = int(size * (1 - valid))
        num_invalid_idx = random.sample(range(size), k=num_invalid)
        for i in num_invalid_idx:
            test_set.loc[i, 'location'] = ", ".join(random.sample(list(gov.ids_by_name), k=2))

    return test_set
