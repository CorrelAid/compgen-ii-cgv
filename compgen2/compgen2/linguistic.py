import string
import random
import compgen2.manipulator

class StringEnriched:
    def __init__(self, string_: str) -> None:
        self.string_ = string_
        self.words = []
        self.chars = []

    def get_string(self) -> str:
        return self.string_

    def apply_manipulator(self, manipulator: compgen2.manipulator.Manipulator):
        if manipulator.type == "char":
            self.manipulate_by_chars(manipulator)
        if manipulator.type == "word":
            self.manipulate_by_words(manipulator)

    def manipulate_by_chars(self, manipulator: compgen2.manipulator.Manipulator):
        chars_modified = []
        for c in list(self.string_):
            if random.random() < manipulator.chance:
                chars_modified.append(manipulator.m(c))
            else:
                chars_modified.append(c)
        self.string_ = "".join(chars_modified)

    def manipulate_by_words(self, manipulator: compgen2.manipulator.Manipulator):
        words = self.decompose(self.string_)
        words_modified = []
        for w in words:
            if self.type_code(w) == "char" and random.random() < manipulator.chance:
                words_modified.append(manipulator.m(w))
            else:
                words_modified.append(w)
        self.string_ = "".join(words_modified)

    def decompose(self, s: str) -> list[str]:
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
    def type_code(s:str) -> int:
        if (s[0] in string.punctuation or s[0] in string.whitespace) and s[0] != ".":
            return "punctuation"
        elif s[0] == ".":
            return "period"
        else:
            return "char"
