from collections import defaultdict, Counter, deque
import string
import enchant
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tag import pos_tag
from spellcheck.spellchecker import SpellChecker, SpellingCorrection
from spellcheck.parse_util import word_tokenize
from spellcheck.constants import contractions


class EditDistanceSpellChecker(SpellChecker):

    def __init__(self, error_model, lang_model):
        """
        Construct EditDistanceSpellChecker.

        Params:
            error_model: [EditPdist] An estimated probability distribution
                for types of edits, P(w | c).
            lang_model: [LanguageModel] An estimated probability distribution for
                words, P(c).
        """
        self.lang_model = lang_model
        self.error_model = error_model
        self.eng_us_dict = enchant.Dict('en_US')
        self.eng_gb_dict = enchant.Dict('en_GB')
        words = set(nltk.corpus.words.words()).union(contractions)
        self.prefixes = set(w[:i] for w in words for i in range(len(w) + 1))
        self.alphabet = string.ascii_lowercase + '\''

    def should_correct(self, word, tag, context):
        """Return if a word should be corrected or not"""
        if tag and tag == 'NNP':
            return False
        return (self.valid_format_for_correction(word)
                and not self.in_dict(word)
                and not self.common_word(word, context))

    def in_dict(self, word):
        if word:
            return self.eng_us_dict.check(word) or self.eng_gb_dict.check(word)
        return False

    def common_word(self, word, context):
        return self.lang_model.prob(word, context) > 0.0001

    def valid_format_for_correction(self, word):
        """Return if a word should be considered for correction."""
        return (len(word) > 1 and word.isalpha()
            and not any([char.isupper() for char in word[1:]]))

    def is_capitalized(self, word):
        return word[0].isupper()

    def capitalize(self, word):
        """Returns word capitalized"""
        return word[0].upper() + word[1:]

    def get_edit(self, misspelled, correct):
        """Get edit string from mispelled and correct character changes."""
        return misspelled + '|' + correct

    def edits(self, head, tail, max_edits, edits, results):
        ## Based on http://norvig.com/ngrams/ ##
        correction = head+tail
        if self.in_dict(correction):
            edit_string = '+'.join(edits)
            if correction not in results:
                results[correction] = edit_string
            else:
                results[correction] = max(
                    results[correction], edit_string, key=self.error_model.prob)
        if max_edits <= 0:
            return results
        # Only try insertion on extensions that are possible prefixes of words
        extensions = [head + c for c in self.alphabet if head + c in self.prefixes]
        prev_char = (head[-1] if head else '<')
        # Insertion
        for ext in extensions:
            results = self.edits(ext, tail, max_edits - 1, edits + [
                self.get_edit(prev_char, prev_char + ext[-1])], results)
        if not tail:
            return results
        # Deletion
        results = self.edits(head, tail[1:], max_edits - 1,
            edits + [self.get_edit(prev_char + tail[0], prev_char)], results)
        for ext in extensions:
            if ext[-1] == tail[0]: # Match
                results = self.edits(ext, tail[1:], max_edits, edits, results)
            else: # Replacement
                results = self.edits(ext, tail[1:], max_edits - 1, edits +
                    [self.get_edit(tail[0], ext[-1])], results)
        # Transpose
        if len(tail)>=2 and tail[0]!=tail[1] and head+tail[1] in self.prefixes:
            results = self.edits(head+tail[1], tail[0]+tail[2:], max_edits - 1,
                edits + [self.get_edit(tail[0:2], tail[1]+tail[0])], results)
        return results

    def get_candidates(self, word, max_edits=1):
        "Return a dict of {correcion: edit} pairs within d edits of word."
        return self.edits('', word, max_edits, [], {})

    def correct(self, word, tag, context):
        """Returns a correction for word."""
        candidates = self.get_candidates(word)
        if word not in candidates:
            candidates[word] = ''
        # Prevent correcting plural nouns into singular nouns
        if ((tag == 'NNS' or tag == 'NNPS')
            and word[-1] == 's' and word[:-1] in candidates):
            candidates.pop(word[:-1])
        #print(word)
        #for c, e in candidates.items():
        #    prob_c = self.lang_model.prob(c, context)
        #    prob_e = self.error_model.prob(e)
        #    print(c, prob_c, e, prob_e, prob_c * prob_e)
        best_correction, edit = max(
            candidates.items(), key=(lambda c: self.score_correction(c, context)))
        return best_correction

    def score_correction(self, candidate, context):
        """
        Score a candidate correction.

        Params:
            candidate: [(string, string)] A tuple containing the correction and
                the edit string.
            context: [deque] The n - 1 words before candidate where n is the
                order of the lang model.

        Returns:
            [float] The score for the correction.  Larger scores are
                better.
        """
        correction, edit = candidate
        return self.lang_model.prob(correction, context) * self.error_model.prob(edit)

    def correct_with_capitalization(self, word, tag, context):
        correction = self.correct(word.lower(), tag, context)
        if correction and self.is_capitalized(word):
           correction = self.capitalize(correction)
        return correction

    def spellcheck(self, dataset):
        corrections = []
        for text in dataset:
            sentences = sent_tokenize(text)
            # Check quality of POS tagging
            tagged_words = [(word, tag) for sent in sentences for
                (word, tag) in pos_tag(word_tokenize(sent))]
            text_corrections = []
            context = deque([''] * (self.lang_model.order() - 1))
            for ind, tagged_word in enumerate(tagged_words):
                word, tag = tagged_word
                if self.should_correct(word, tag, context):
                    word_corrected = self.correct_with_capitalization(word, tag,
                            context)
                    if word_corrected != word:
                        text_corrections.append(SpellingCorrection(ind, word,
                            [word_corrected]))
                if context:
                    context.popleft()
                    context.append(word)
            corrections.append(text_corrections)
        return corrections

    def __str__(self):
        return self.__class__.__name__
