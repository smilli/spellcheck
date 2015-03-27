from spellchecker import SpellChecker, SpellingCorrection
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from collections import defaultdict, Counter
import string

class CorpusSpellChecker(SpellChecker):

    def __init__(self, dataset, edit_pdist, corpus_names=None):
        """
        Construct CorpusSpellChecker.

        Params:
            dataset: [list of strings] The essays to correct.
            edit_pdist: [EditProbDist obj] An estimated probability distribution
                for types of edits.
            corpus_names: [list of strings] Names of NLTK corpora to use.
                Ex: ['gutenberg', 'brown'] Default is to use only Gutenberg.
        """
        self.dataset = dataset
        if not corpus_names:
            corpus_names = ['gutenberg']
        self.corpus_names = corpus_names
        try:
            self.corpus = defaultdict(lambda: 1)
            for corpus_name in corpus_names:
                corpus = getattr(nltk.corpus, corpus_name)
                for word in corpus.words():
                    self.corpus[word.lower()] += 1
        except AttributeError:
            raise Exception('You must provide a valid corpus name')
        self.eng_dict = set(w.lower() for w in nltk.corpus.words.words())
        self.prefixes = set(
            w[:i] for w in self.eng_dict for i in range(len(w) + 1))
        self.edit_pdist = edit_pdist
        self.alphabet = string.ascii_lowercase + '\''

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

    def is_punctuation_mark(self, word):
        # Assumes any word that only has non-alpha chars is a punctuation mark
        return all(not char.isalpha() for char in word)

    def is_capitalized(self, word):
        return word[0].isupper()

    def capitalize(self, word):
        """Returns word capitalized"""
        return word[0].upper() + word[1:]

    def get_edit(self, misspelled, correct):
        """Get edit string from mispelled and correct character changes."""
        return misspelled + '|' + correct

    def edits_r(self, head, tail, max_edits, edits, results):
        correction = head+tail
        if correction in self.eng_dict:
            edit_string = '+'.join(edits)
            results[correction] = max(
                results[correction], edit_string, key=self.edit_pdist.prob)
        if max_edits <= 0:
            return results
        # Only try insertion on extensions that are possible prefixes of words
        extensions = [head + c for c in self.alphabet if head + c in self.prefixes]
        prev_char = (head[-1] if head else '<')
        # Insertion
        for ext in extensions:
            results = self.edits_r(ext, tail, max_edits - 1, edits + [
                self.get_edit(prev_char, prev_char + ext[-1])], results)
        if not tail:
            return results
        ## Deletion
        results = self.edits_r(head, tail[1:], max_edits - 1,
            edits + [self.get_edit(prev_char + tail[0], prev_char)], results)
        for ext in extensions:
            if ext[-1] == tail[0]: ## Match
                results = self.edits_r(ext, tail[1:], max_edits, edits, results)
            else: ## Replacement
                results = self.edits_r(ext, tail[1:], max_edits - 1, edits +
                    [self.get_edit(tail[0], ext[-1])], results)
        ## Transpose
        if len(tail)>=2 and tail[0]!=tail[1] and head+tail[1] in self.prefixes:
            results = self.edits_r(head+tail[1], tail[0]+tail[2:], max_edits - 1,
                edits + [self.get_edit(tail[0:2], tail[1]+tail[0])], results)
        return results

    def edits(self, word, max_edits=2):
        "Return a dict of {correct: edit} pairs within d edits of word."
        return self.edits_r('', word, max_edits, [], defaultdict(lambda: ''))

    def correct(self, word):
        """Returns a correction for word."""
        candidates = self.edits(word)
        if word not in candidates:
            candidates[word] = ''
        best_correction, edit = max(
            candidates.items(),
            key=(lambda c: self.corpus[c[0]] * self.edit_pdist.prob(c[1])))
        return best_correction

    def correct_with_capitalization(self, word):
        correction = self.correct(word.lower())
        if correction and self.is_capitalized(word):
           correction = self.capitalize(correction)
        return correction

    def spellcheck(self):
        corrections = []
        for text in self.dataset:
            sentences = sent_tokenize(text)
            tagged_words = [(word, tag) for sent in sentences for
                    (word, tag) in pos_tag(word_tokenize(sent)) if not
                    self.is_punctuation_mark(word)]
            text_corrections = []
            for ind, tagged_word in enumerate(tagged_words):
                word, tag = tagged_word
                if self.should_correct(word, tag):
                    word_corrected = self.correct_with_capitalization(word)
                    if word_corrected != word:
                        text_corrections.append(SpellingCorrection(ind, word,
                            [word_corrected]))
            corrections.append(text_corrections)
        return corrections

    def __str__(self):
        return self.__class__.__name__
