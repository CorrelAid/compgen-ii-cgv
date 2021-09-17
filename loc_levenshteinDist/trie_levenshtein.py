import time
import sys
DICTIONARY = "compgen-ii-cgv/data/gov_dictionary.txt"
TARGET = "aaachen"
MAX_COST = 1
# Keep some interesting statistics
NodeCount = 0
WordCount = 0


# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

        global NodeCount

    def insert(self, word):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.word = word
