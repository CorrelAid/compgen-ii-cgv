import random
import pandas as pd
from collections import defaultdict
from . import Manipulator
from . import StringEnriched
from .. import GOV
from .. import const_synthetic 
#import compgen2.string_utils.linguistic
#import compgen2.string_utils.manipulator

random.seed(1337)

class Synthetic:
    def __init__(self, gov: GOV) -> None:
        self.gov = gov
        self.locations = []
        self.locations_synthetic = []
        self.fractal_dict = self._fractal_dict()
        self.lino_dict = self._linotype_dict()
        self.m_linotype = Manipulator(self.linotype, "char", const_synthetic.P_LINO)
        self.m_fractal = Manipulator(self.fractal, "char", const_synthetic.P_FRACTAL)
        self.m_drop = Manipulator(self.drop, "char", const_synthetic.P_DROP)
        self.m_shorten = Manipulator(self.shorten, "word", const_synthetic.P_SHORTEN)
        self.COMBO_TEST = [self.m_linotype, self.m_fractal, self.m_drop, self.m_shorten]
        self.MANIPULATION_COMBOS = [self.COMBO_TEST]
    
    def create_synthetic_data(self, size: int):
        paths_ids = list(self.gov.all_paths)[:size]
        paths_names = [self.gov.decode_path_name(p) for p in paths_ids]
        for p in paths_names:
            location = self.create_location_from_path(p)
            self.locations.append(", ".join(location))
            location = self.shuffle_order(location)
            se = StringEnriched(", ".join(location))
            for combo in self.MANIPULATION_COMBOS:
                se = self.manipulate(se, combo)
            self.locations_synthetic.append(se)

        for pair in zip(self.locations, self.locations_synthetic):
            print(pair[0])
            print(pair[1])
    
    def _linotype_dict(self) -> dict[str, set[str]]:
        """
        Create a mapping from a character to all its neighboured characters on the linotype keyboard
        """
        lino_dict = defaultdict(set)
        rows = len(const_synthetic.key_matrix_linotype_reduced)
        cols = len(const_synthetic.key_matrix_linotype_reduced[0])
        for i in range (rows):
            for j in range (cols):
                c = const_synthetic.key_matrix_linotype_reduced[i][j]
                if i > 0:    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i-1][j]}
                if j > 0:    lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i][j-1]}
                if j < cols-1: lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i][j+1]}
                if i < rows-1: lino_dict[c] |= {const_synthetic.key_matrix_linotype_reduced[i+1][j]}
                lino_dict[c].difference_update({'@'})
                digits = {str(n) for n in range(10)}
                if c in digits:
                    lino_dict[c].intersection_update(digits)
                else:
                    lino_dict[c].difference_update(digits)
        del(lino_dict['@'])
        lino_dict.default_factory = None
        return lino_dict

    def _fractal_dict(self) -> dict[str, set[str]]:
        """
        Create a mapping from a letter all letters that are visually similar in fractal font
        """
        fractal_dict = defaultdict(set)
        for p in const_synthetic.fractal_confusion_pairs:
            fractal_dict[p[0]] |= {p[1]}
            fractal_dict[p[1]] |= {p[0]}
        fractal_dict.default_factory = None
        return fractal_dict

    def create_location_from_path(self, p: tuple) -> list:
        """
        Picks two objects from a tuple (one in case of len(p)==1)
        Args:
          p: tuple
        Returns
          locations: list
        """
        locations = []
        locations.append(random.choice(p[-2:]))
        if len(p) > 1:
            locations.append(random.choice(p[:-2]))
        return locations

    def shuffle_order(self, l: list) -> list:
        """
        Shuffle a list of objects in place
        Args:
          l: list
        """
        if random.random() < const_synthetic.P_SHUFFLE:
            return l[::-1]
        else:
            return l

    def manipulate(self, se: StringEnriched, manipulation_combo: list[Manipulator]) -> str:
        """
        Manipulate a string given a collection of manipulators
        """
        
        for m in manipulation_combo:
            se.apply_manipulator(m)
        return se.get_string()

    def shorten(self, w: str) -> str:
        """
        Word-based.
        Drop the last n characters of a word where n is randomly chosen. Insert a period after the word in case it does not yet exist.
        """
        if len(w) > 1:
            c = random.randint(1,len(w)-1)
            return w[0:c] + "."
        else:
            return w
        #if r+1 == len(l) or l[r+1] != ".":
        #    l.insert(r+1,".")         

    def linotype(self, c:str) -> str:
        """
        Character-based.
        """
        return random.choice(list(self.lino_dict.get(c,{c}))) ## choose a random neighboured key
    
    def fractal(self, c:str) -> str:
        """
        Character-based.
        """
        return random.choice(list(self.fractal_dict.get(c,{c}))) ## choose a random similar letter

    def drop(self, _:str) -> str:
        """
        Character-based.
        """
        return ""



def build_test_set(gov, size: int, num_parts: int = 2, valid: float = 1):
    test_set = []
    population = [p for p in gov.all_paths if 190315 in p and len(p) >= num_parts]
    
    samples = random.sample(population=population, k=size)
    for sample in samples:
        while True:
            sample_nodes = random.sample(sample, k=num_parts)
            try:
                test_set.append(
                    ", ".join(
                        map(
                            lambda id_: random.sample(list(gov.names_by_id[id_]), k=1)[
                                0
                            ],
                            sample_nodes,
                        )
                    )
                )
                break
            except KeyError:
                pass

    if valid < 1:
        num_invalid = int(size * (1 - valid))
        num_invalid_idx = random.sample(range(size), k=num_invalid)
        for i in num_invalid_idx:
            test_set[i] = ", ".join(random.sample(list(gov.names.content.values), k=2))

    return pd.Series(test_set, name="location")