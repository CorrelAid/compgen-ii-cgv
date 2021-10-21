#from Levenshtein import distance
from functools import lru_cache

from trie_levenshtein import TrieNode


class LocCorrection:
    # To Do
    @lru_cache(1000000)
    def __init__(self, loc_list):
        """
        :param loc_list:  list of string
        """
        self.loc_list = loc_list
        self.word_count = 0
        self.trie = TrieNode()
        self._list2trie()

    def _list2trie(self):
        # read dictionary file into a trie
        for word in self.loc_list:
            self.word_count += 1
            self.trie.insert(word.lower())
        # The search function returns a list of all words that are less than the given
        # maximum distance from the target word

    def search(self, word, maxCost):
        """

        :param word: string
        :param cost: supports int, range, or dictionary (key: regex, value: range/int)
        param exclude_operations: None / subset of ["insert", "delete", "replace"]
        :return:
        """
        # build first row
        word = word.lower()
        currentRow = range(len(word) + 1)
        results = []
        # recursively search each branch of the trie
        for letter in self.trie.children:
            self._searchRecursive(
                self.trie.children[letter],
                letter,
                word,
                currentRow,
                results,
                maxCost
            )
        return results

    #def cal_levenstein(self, word):
        # This recursive helper is used by the search function above. It assumes that
        # the previousRow has been filled in already.
    #    return [distance(word.lower(), i.lower()) for i in self.loc_list]

    def _searchRecursive(
        self, node, letter, word, previousRow, results, maxCost):
        columns = len(word) + 1
        currentRow = [previousRow[0] + 1]
        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range(1, columns):
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1
            if word[column - 1] != letter:
                replaceCost = previousRow[column - 1] + 1
            else:
                replaceCost = previousRow[column - 1]

            currentRow.append(min(insertCost, deleteCost,replaceCost ))
        # if the last entry in the row indicates the optimal cost is less than the
        # defined cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word != None:
            if len(results)!=0 and currentRow[-1] > results[-1][1]:
                pass
            else:
                results.append((node.word, currentRow[-1]))
        # recursively search each branch of the trie
        if min(currentRow) <= maxCost:
            for letter in node.children:
                self._searchRecursive(node.children[letter], letter, word, currentRow,
                                results, maxCost)
        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie


lC = LocCorrection(("aachen", "preussen", "ahen")) #groudtruth / gov
#vague match input
results = lC.search("aaashen", 5)
print('value search', results)

import pandas as pd
#df = pd.read_parquet(r"C:\Users\A111519951\PycharmProjects\correlaid\compgen-ii-cgv\data\deutsche-verlustlisten-1wk_preprocessed.parquet").head(100)
#gov_df = pd.read_parquet(r"C:\Users\A111519951\PycharmProjects\correlaid\compgen-ii-cgv\data\gov_orte_v01_preprocessed.parquet").head(100)
lC = LocCorrection(tuple(["neustatb", "neustata", "neustatttt", "neustattttt"])) #groudtruth / gov
#vague match input
results = lC.search("Neustatt", 8)
print('value search', results)

