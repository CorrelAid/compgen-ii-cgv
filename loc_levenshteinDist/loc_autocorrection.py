from trie_levenshtein import TrieNode

class LocCorrection:
    def __init__(self, dictionary):
        """
        :param dictionary: dict item, (key, value)-> (id, word)
        """
        self. dictionary = dictionary
        self.WordCount = 0
        self.trie = TrieNode()
        self._dict2trie()
        self.reverse_dictionary = {v:k for (k,v) in self.dictionary.items()}

    def _dict2trie(self):
        # read dictionary file into a trie
        for word in self.dictionary.values():
            self.WordCount += 1
            self.trie.insert(word.lower())
        print("Read %d words" % (self.WordCount))

        # The search function returns a list of all words that are less than the given
        # maximum distance from the target word
    def search(self, word, maxCost):
        # build first row
        currentRow = range(len(word) + 1)
        results = []
        # recursively search each branch of the trie
        for letter in self.trie.children:
            self._searchRecursive(
                self.trie.children[letter], letter, word, currentRow, results, maxCost
            )
        return results

        # This recursive helper is used by the search function above. It assumes that
        # the previousRow has been filled in already.
    def _searchRecursive(self, node, letter, word, previousRow, results, maxCost):
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
            currentRow.append(min(insertCost, deleteCost, replaceCost))
        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word != None:
            results.append((node.word, self.reverse_dictionary[node.word], currentRow[-1]))
        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min(currentRow) <= maxCost:
            for letter in node.children:
                self._searchRecursive(
                    node.children[letter], letter, word, currentRow, results, maxCost
                    )

# example
lC = LocCorrection({"abc":'aachen'})
results = lC.search("aaachen", 1)
print(results)
