from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from edit_dist_spellchecker import EditDistanceSpellChecker

## This is totally experimental & likely to completely change in future ##
class WordSimilaritySpellChecker(EditDistanceSpellChecker):

    def __init__(self, dataset, edit_pdist, word_pdist):
        super().__init__(dataset, edit_pdist, word_pdist)
        self.top_word_senses = self.extract_top_word_senses()

    def extract_top_word_senses(self, num_words=10):
        """
        Extract the most important words from a dataset.

        Returns:
            [list of Synsets] The top num_words words.
        """
        word_senses = Counter()
        for essay in self.dataset:
            words = [word.lower() for word in word_tokenize(essay) if not
                        self.is_punctuation_mark(word)]
            for word in words:
                if word not in stopwords.words():
                    sense = self.get_first_sense(word)
                    if sense:
                        word_senses[sense] += 1
        return [s for s, c in word_senses.most_common(num_words)]

    def get_first_sense(self, word):
        senses = wn.synsets(word)
        if senses:
            return senses[0]
        return None

    def similarity_to_dataset(self, word, sense=None):
        """
        Compute the similarity of a word to the other words in a dataset.

        Params:
            word: [string] The word to compute similarity for.
            sense: [string] The word sense of the word if known.

        Returns:
            similarity: [float] A similarity score between 0 and 1, where a
                higher score indicates higher similarity.
        """
        if not sense:
            # Pick first sense
            sense = self.get_first_sense(word)
            if not sense:
                # TODO(smilli): Figure out what to do here
                return 0
        similarity = 0
        for top_word_sense in self.top_word_senses:
            path_sim = wn.path_similarity(top_word_sense, sense)
            if path_sim:
                similarity += path_sim
        similarity /= len(self.top_word_senses)
        return similarity

    def score_correction(self, candidate):
        """
        Score a candidate correction.

        Params:
            candidate: [(string, string)] A tuple containing the correction and
                the edit string.

        Returns:
            [float] The score for the correction.  Larger scores are
                better.
        """
        correction, edit = candidate
        return (self.similarity_to_dataset(correction) *
            self.word_pdist.prob(correction) * self.edit_pdist.prob(edit))
