import string
import random
from . import Manipulator

class StringEnriched:
    def __init__(self, string_: str) -> None:
        self.string_ = string_
        self.words = []
        self.chars = []

    def get_string(self) -> str:
        return self.string_

    def apply_manipulator(self, manipulator: Manipulator, distortion_factor: float = 1.) -> None:
        """Take a manipulator object and apply internally on the string
        Args:
          manipulator (Manipulator): A single mainpulator object that is applied on self.string_
        """
        if manipulator.type == "char":
            self.manipulate_by_chars(manipulator, distortion_factor)
        if manipulator.type == "word":
            self.manipulate_by_words(manipulator, distortion_factor)

    def manipulate_by_chars(self, manipulator: Manipulator, distortion_factor: float = 1.) -> None:
        """Take a manipulator object of type "char" and apply it internally on self.string_
        Args:
          manipulator (Manipulator): A single mainpulator object that is applied on self.string_
        """
        chars_modified = []
        for c in list(self.string_):
            if random.random() < manipulator.chance * distortion_factor:
                chars_modified.append(manipulator.m(c))
            else:
                chars_modified.append(c)
        self.string_ = "".join(chars_modified)

    def manipulate_by_words(self, manipulator: Manipulator, distortion_factor: float = 1.) -> None:
        """Take a manipulator object of type "word" and apply it internally on self.string_
        Args:
          manipulator (Manipulator): A single mainpulator object that is applied on self.string_
        """
        words = self.decompose(self.string_)
        words_modified = []
        for w in words:
            if self.type_code(w) == "alphanumerical" and random.random() < manipulator.chance * distortion_factor:
                words_modified.append(manipulator.m(w))
            else:
                words_modified.append(w)
        self.string_ = "".join(words_modified)

    def decompose(self, s: str) -> list[str]:
        """Partition a string into a list of strings where each individual string has its on type based on type_code()
        Args:
          s (str): A string
        Returns:
          l (list[str]): A partition of the input string s based on type_code()
        """
        l = []
        t_curr = None
        t_prev = None
        for c in s:
            t_curr = self.type_code(c)
            if t_curr == t_prev:
                l[-1] += c
            else:
                l.append(c)
            t_prev = t_curr
        return l

    @staticmethod
    def type_code(s:str) -> str:
        """
        Return the type of a string based on its first letter. The three types are:
        - string.punctuation (without the period)
        - period '.'
        - Any other unicode characters not covered by string.punctuation.
        Args:
          s (str): A string
        Returns
          type (str): One of the three values 'punctuation', 'period', 'alphanumerical'
        """
        if (s[0] in string.punctuation or s[0] in string.whitespace) and s[0] != ".":
            return "punctuation"
        elif s[0] == ".":
            return "period"
        else:
            return "alphanumerical"
