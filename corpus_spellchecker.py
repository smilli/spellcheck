from spellchecker import SpellChecker, SpellingCorrection
import nltk
import nltk.corpus
from nltk.tokenize import word_tokenize
import string

class CorpusSpellChecker(SpellChecker):

    def __init__(self, corpus_name=None):
        """
        Construct CorpusSpellChecker.

        Params:
            corpus_name: [string] Name of NLTK corpus to use.  Ex: 'gutenberg'
        """
        self.corpus_name = corpus_name
        try:
            corpus = getattr(nltk.corpus, corpus_name)
            self.corpus = nltk.FreqDist([word.lower() for word in corpus.words()])
        except AttributeError:
            raise Exception('You must provide a valid corpus name')

    def is_valid(self, word):
        """Returns if a word is spelled correctly."""
        return word in self.corpus

    def edit1_words(self, word):
        """Find all strings edit distance of 1 away from word."""
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in
                string.ascii_lowercase if b]
        inserts    = [a + c + b     for a, b in splits for c in
                string.ascii_lowercase]
        return set(deletes + transposes + replaces + inserts)

    def edit2_words(self, word):
        """Find all strings edit distance of 2 away from word."""
        return set(e2 for e1 in self.edit1_words(word) for e2 in self.edit1_words(e1))

    def correct(self, index, word):
        """Returns SpellingCorrection for word."""
        candidates = [w for w in self.edit1_words(word) if self.is_valid(w)]
        if not candidates:
            candidates = [w for w in self.edit2_words(word) if self.is_valid(w)]
        if not candidates:
            correction = word
        else:
            correction = max(candidates, key=self.corpus.get)
        return SpellingCorrection(index, word, [correction])

    def spellcheck(self, dataset):
        corrections = []
        for text in dataset:
            words = [
                (i, w) for (i, w) in enumerate(text.split()) if w.isalpha()]
            corrections.append([self.correct(ind, word) for (ind, word) in
                words if not self.is_valid(word)])
        return corrections

    def __str__(self):
        return '%s %s' % (self.__class__.__name__, self.corpus_name)
