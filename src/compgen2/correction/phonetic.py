import collections
import re


class Phonetic:
    def __init__(self) -> None:
        self.RULES = collections.OrderedDict()
        self.RULES[re.compile(r".[AEIJOUYÄÖÜ].", re.I)]    = "0"
        self.RULES[re.compile(r".[À-ÃÈ-ÏÒ-ÕÙ-Û].", re.I)]  = "0"
        self.RULES[re.compile(r".[B].", re.I)]             = "1"
        self.RULES[re.compile(r".[P][^H]", re.I)]          = "1"
        self.RULES[re.compile(r".[DT][^CSZ]", re.I)]       = "2"
        self.RULES[re.compile(r".[FVW].", re.I)]           = "3"
        self.RULES[re.compile(r".[P][H]", re.I)]           = "3"
        self.RULES[re.compile(r".[GKQ].", re.I)]           = "4"
        self.RULES[re.compile(r"\s[C][AHKLOQRUX]", re.I)]  = "4"
        self.RULES[re.compile(r"[^SZ][C][AHKOQUX]", re.I)] = "4"
        self.RULES[re.compile(r"[^CKQ][X].", re.I)]        = "48"
        self.RULES[re.compile(r".[L].", re.I)]             = "5"
        self.RULES[re.compile(r".[MN].", re.I)]            = "6"
        self.RULES[re.compile(r".[R].", re.I)]             = "7"
        self.RULES[re.compile(r".[SZß].", re.I)]           = "8"
        self.RULES[re.compile(r"[SZ][C].", re.I)]          = "8"
        self.RULES[re.compile(r"\s[C][^AHKLOQRUX]", re.I)] = "8"
        self.RULES[re.compile(r"[C][^AHKOQUX]", re.I)]     = "8"
        self.RULES[re.compile(r".[DT][CSZ]", re.I)]        = "8"
        self.RULES[re.compile(r"[CKQ][X].", re.I)]         = "8"

        self.SPECIAL_CHARACTER = re.compile(r"[^a-zäöüß\sà-ãè-ïò-õù-û]", re.I)
        
        self.names_by_phonetic = {}
        
    def build_phonetic_index(self, names: list[str]):
        self.names_by_phonetic = collections.defaultdict(set)
        for name in names:
            self.names_by_phonetic[self.encode(name)] |= {name}
        
        self.names_by_phonetic.default_factory = None
        
    def encode(self, inputstring: str) -> str:
        """
        Args:
          inputstring (str)
        Returns:
          Returns the phonetic code of the given inputstring. Kölner Phonetik.
        """

        # remove anything except characters and whitespace
        inputstring = self.SPECIAL_CHARACTER.sub("", inputstring)

        encoded = ""
        for i in range(len(inputstring)):
            part = inputstring[i-1 : i+2]
            # The RULES always expect 3 characters. Hence the beginning and end of inputstring get extendend by a space.
            if len(inputstring) == 1:
                part = f" {inputstring[0]} "
            elif i == 0:
                part = f" {inputstring[:2]}"
            elif i == len(inputstring) - 1:
                part = f"{inputstring[i - 1:]} "

            for rule, code in self.RULES.items():
                if rule.match(part):
                    encoded += code
                    break

        # remove immediately repeated occurrences of phonetic codes
        while [v for v in self.RULES.values() if encoded.find(v*2) != -1]:
            for v in self.RULES.values():
                encoded = encoded.replace(v*2, v)

        if encoded:
            encoded = encoded[0] + encoded[1:].replace("0", "")

        return encoded