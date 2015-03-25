from spellchecker import SpellChecker, SpellingCorrection
import nltk
import nltk.corpus
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import string

class CorpusSpellChecker(SpellChecker):

    def __init__(self, corpus_names=None, use_dict=True):
        """
        Construct CorpusSpellChecker.

        Params:
            corpus_names: [list of string] Names of NLTK corpora to use.
                Ex: ['gutenberg', 'brown'] Default is to use only Gutenberg.
            use_dict: [bool] Whether to filter out words to correct based on
                their appearance in a list of dictionary words
        """
        if use_dict:
            self.eng_dict = set(w.lower() for w in nltk.corpus.words.words())
        if not corpus_names:
            corpus_names = ['gutenberg']
        self.corpus_names = corpus_names
        try:
            corpora = []
            for corpus_name in corpus_names:
                corpora.append(getattr(nltk.corpus, corpus_name))
            self.corpus = nltk.FreqDist([
                word.lower() for corpus in corpora for word in corpus.words()])
        except AttributeError:
            raise Exception('You must provide a valid corpus name')

    def should_correct(self, word, tag=None):
        """Return if a word should be corrected or not"""
        if tag and tag == 'NNP':
            return False
        return (self.valid_format_for_correction(word)
                and not self.in_dict(word)
                and not self.in_corpus(word))

    def in_dict(self, word):
        return word.lower() in self.eng_dict

    def in_corpus(self, word):
        return word.lower() in self.corpus

    def valid_format_for_correction(self, word):
        """Return if a word should be considered for correction."""
        return word.isalpha() and not any([char.isupper() for char in word[1:]])

    def edit1_words(self, word):
        """Find all strings edit distance of 1 away from word."""
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in
                string.ascii_lowercase if b]
        inserts    = [a + c + b for a, b in splits for c in
                string.ascii_lowercase + '\'']
        return set(deletes + transposes + replaces + inserts)

    def edit2_words(self, word):
        """Find all strings edit distance of 2 away from word."""
        return set(e2 for e1 in self.edit1_words(word) for e2 in self.edit1_words(e1))

    def correct(self, word):
        """Returns a correction for word."""
        candidates = [w for w in self.edit1_words(word) if self.in_corpus(w)]
        if not candidates:
            candidates = [
                w for w in self.edit2_words(word) if self.in_corpus(w)]
        if not candidates:
            return None
        else:
            return max(candidates, key=self.corpus.get)

    def is_capitalized(self, word):
        return word[0].isupper()

    def capitalize(self, word):
        """Returns word capitalized"""
        return word[0].upper() + word[1:]

    def correct_with_capitalization(self, word):
        correction = self.correct(word.lower())
        if correction and self.is_capitalized(word):
           correction = self.capitalize(correction)
        return correction

    def is_punctuation_mark(self, word):
        # Assumes any word that only has non-alpha chars is a punctuation mark
        return all(not char.isalpha() for char in word)

    def spellcheck(self, dataset):
        corrections = []
        for text in dataset:
            sentences = sent_tokenize(text)
            tagged_words = [(word, tag) for sent in sentences for
                    (word, tag) in pos_tag(word_tokenize(sent)) if not
                    self.is_punctuation_mark(word)]
            text_corrections = []
            for ind, tagged_word in enumerate(tagged_words):
                word, tag = tagged_word
                if self.should_correct(word, tag):
                    word_corrected = self.correct_with_capitalization(word)
                    if word_corrected:
                        text_corrections.append(SpellingCorrection(ind, word,
                            [word_corrected]))
            corrections.append(text_corrections)
        return corrections

    def __str__(self):
        return self.__class__.__name__
