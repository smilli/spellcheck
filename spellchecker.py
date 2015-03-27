from operator import xor

class SpellChecker:
    """Abstract class for SpellChecker"""

    def __init__(self, dataset):
        """
        Params:
            dataset: [list of strings] List of texts in data.
        """
        pass

    def spellcheck(self):
        """
        Check spelling of all texts in dataset.

        Returns:
            List of lists of SpellingCorrection objects.
        """
        pass

class SpellingCorrection:

    def __init__(self, index, word, corrections):
        """
        Constructor for SpellingCorrection.

        Params:
            index: [int] index of word in text.
            word: [string] misspelling.
            corrections: [list of strings] list of pos corrections sorted from
                highest to lowest probability.
        """
        self.index = index
        self.word = word
        self.corrections = corrections

    @property
    def best_correction(self):
        if not self.corrections:
            return None
        return self.corrections[0]

    def __str__(self):
        return 'Incorrect word: %s at index %s.  Corrections: %s' % (self.word,
                self.index, self.corrections)

    def __eq__(self, other):
        return (self.index == other.index and self.word == other.word and
                self.best_correction == other.best_correction)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return xor(hash(self.index), xor(hash(self.word),
            hash(self.best_correction)))
