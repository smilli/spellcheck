from nltk.tokenize import sent_tokenize
from spellcheck.parse_util import word_tokenize
from spellcheck.spellchecker import SpellChecker, SpellingCorrection
from spellcheck.interactive_corrector import DistMatrix, InteractiveCorrector
from pyxdameraulevenshtein import damerau_levenshtein_distance

class ClusterSpellChecker(SpellChecker):

    def __init__(self, correct_capitalization=False):
        self.rules = {}
        self.correct_capitalization = correct_capitalization

    def save_rules_from_dataset(self, dataset):
        dataset_words = []
        for essay in dataset:
            sents = sent_tokenize(essay)
            dataset_words += [w for sent in sents for w in word_tokenize(sent) if
                    w.isalpha() and not any([char.isupper() for char in w[1:]])]
        corrector = InteractiveCorrector(
                DistMatrix(dataset_words, damerau_levenshtein_distance))
        rules = corrector.extract_rules()
        self.rules = dict((w, c) for w, c in rules.items() if
                self.valid_correction(w, c))
        return self.rules

    def is_punctuation_mark(self, word):
        # Assumes any word that only has non-alpha chars is a punctuation mark
        return all(not char.isalpha() for char in word)

    def valid_correction(self, word, correction):
        return (self.correct_capitalization or not ((word[0].upper() + word[1:] ==
            correction) or (word == correction[0].upper() + correction[1:])))

    def spellcheck(self, dataset):
        corrections = []
        for text in dataset:
            essay_corrections = []
            sentences = sent_tokenize(text)
            words  = [w for sent in sentences for w in word_tokenize(sent)
                    if not self.is_punctuation_mark(w)]
            for i, word in enumerate(words):
                if word in self.rules:
                    essay_corrections.append(SpellingCorrection(i, word,
                        [self.rules[word]]))
            corrections.append(essay_corrections)
        return corrections
