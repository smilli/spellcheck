class SpellChecker:
    """Abstract class for SpellChecker"""

    def __init__(self, dataset=None):
        """
        Constructor for SpellChecker.

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
