from collections import Counter
import enchant
from nltk.tokenize import sent_tokenize
from spellcheck.parse_util import word_tokenize
from spellcheck.spellchecker import SpellChecker, SpellingCorrection
from spellcheck.interactive_corrector import DistMatrix, InteractiveCorrector
from pyxdameraulevenshtein import damerau_levenshtein_distance

class ClusterSpellChecker(SpellChecker):

    def __init__(self, correct_capitalization=False):
        self.eng_us_dict = enchant.Dict('en_US')
        self.eng_gb_dict = enchant.Dict('en_GB')
        self.rules = {}
        self.correct_capitalization = correct_capitalization

    def save_edit1_rules(self, dataset):
        """
        Add rules for dataset words that are an edit distance of 1 away from
        misspelled dataset words.
        """
        # TODO(smilli): Make overrwrite rules
        dataset_words = []
        for essay in dataset:
            sents = sent_tokenize(essay)
            dataset_words += [w for sent in sents for w in word_tokenize(sent) if
                self.valid_word(w)]
        # TODO(smilli): filter out non dict words that are still
        # correct (proper nouns)
        corrector = InteractiveCorrector(
                DistMatrix(dataset_words, damerau_levenshtein_distance))
        rules = corrector.extract_rules()
        self.rules = dict((w, c) for w, c in rules.items() if
                self.valid_correction(w, c))
        return self.rules

    def save_suggested_rules(self, dataset):
        """
        Add rules for dataset words that are suggested corrections for
        misspelled dataset words.
        """
        dataset_words = []
        for essay in dataset:
            sents = sent_tokenize(essay)
            dataset_words += [w for sent in sents for w in word_tokenize(sent) if
                self.valid_word(w)]
        dataset_word_freqs = Counter(dataset_words)
        for word in set(dataset_words):
            if self.valid_word(word) and not self.in_dict(word):
                # TODO(smilli): filter out non dict words that are still
                # correct (proper nouns)
                suggestions = self.get_suggestions(word)
                total_freq = sum(dataset_word_freqs[s] for s in
                    suggestions)
                correction = None
                if total_freq > 0:
                    for suggestion in suggestions:
                        if dataset_word_freqs[suggestion]/total_freq >= 0.5:
                            correction = suggestion
                            break
                if correction and self.valid_correction(word, correction):
                    self.rules[word] = correction

    def remove_saved_rules(self):
        self.rules = {}

    def valid_word(self, word):
        """
        Return whether the token is a valid word.
        """
        return (word.isalpha() and not any([char.isupper() for char in
            word[1:]]))

    def valid_correction(self, word, correction):
        return (self.correct_capitalization or not ((word[0].upper() + word[1:] ==
            correction) or (word == correction[0].upper() + correction[1:])))

    def get_suggestions(self, word):
        suggestions = set(self.eng_us_dict.suggest(word)).union(
            set(self.eng_gb_dict.suggest(word)))
        return suggestions

    def in_dict(self, word):
        if word:
            return self.eng_us_dict.check(word) or self.eng_gb_dict.check(word)
        return False

    def spellcheck(self, dataset):
        corrections = []
        for text in dataset:
            essay_corrections = []
            sentences = sent_tokenize(text)
            words  = [w for sent in sentences for w in word_tokenize(sent)]
            for i, word in enumerate(words):
                if word in self.rules:
                    essay_corrections.append(SpellingCorrection(i, word,
                        [self.rules[word]]))
            corrections.append(essay_corrections)
        return corrections
