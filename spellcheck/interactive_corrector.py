import argparse
import enchant
import numpy as np
from collections import Counter
from nltk import sent_tokenize, word_tokenize
from spellcheck.parse_util import DigitizationParser
from pyxdameraulevenshtein import damerau_levenshtein_distance
from prettytable import PrettyTable
parser = argparse.ArgumentParser(description='Cluster ngrams in a dataset.')
parser.add_argument('-d', '--dataset', help='Path to dataset file.',
        required=True)
parser.add_argument('-f', '--save-file', help='Path to file to save rules to.')


class DistMatrix:

    def __init__(self, words, compute_distance):
        """
        Construct DistMatrix.

        Params:
            words: [list] list of words
            compute_distance: [func] function that takes two words as arguments
                and returns the distance between them.
        """
        self.words_counter = Counter(words)
        self.words = list(set(words))
        self.words_to_ind = dict((w, i) for i, w in enumerate(self.words))
        indices = np.triu_indices(len(self.words), 1)
        self.pairwise_dists = np.apply_along_axis(
            lambda col: compute_distance(
                self.words[col[0]], self.words[col[1]]),
            0, indices)
        pairs = ((i1, i2) for i1, i2 in zip(indices[0], indices[1]))
        self.pairs_to_ind = dict((p, i) for i, p in enumerate(pairs))

    def pair_to_dist(self, w1, w2):
        w1_ind = self.words_to_ind[w1]
        w2_ind = self.words_to_ind[w2]
        pair = (w1_ind, w2_ind) if w1_ind < w2_ind else (w2_ind, w1_ind)
        return self.pairwise_dists[self.pairs_to_ind[pair]]

    def get_words(self):
        """Get all words in matrix."""
        return self.words

    def get_close_words(self, word, max_dist):
        """
        Get all words within max_dist of given word.

        The current word will be returned in the list of close words.

        Params:
            word: [string] The word to find close words to.
            max_dist: [float] Maximum distance a word can be from given word to
                be considered a close word.

        Returns:
            close_words [list] List of tuples of form (close word,
             num occurence of close word)
        """
        close_words = [(word, self.words_counter[word])]
        for other_word in self.words:
            if other_word != word:
                dist = self.pair_to_dist(word, other_word)
                if dist <= max_dist:
                    close_words.append(
                        (other_word, self.words_counter[other_word]))
        return close_words


class InteractiveCorrector:

    def __init__(self, matrix):
        self.d_matrix = matrix
        self.eng_us_dict = enchant.Dict('en_US')
        self.eng_gb_dict = enchant.Dict('en_GB')

    def in_dict(self, word):
        if word:
            return self.eng_us_dict.check(word) or self.eng_gb_dict.check(word)
        return False

    def extract_rules(self, save_file_path):
        rules = {}
        if save_file_path:
            save_file = open(save_file_path, 'a')
        for word in self.d_matrix.get_words():
            if not self.in_dict(word):
                close_words = self.d_matrix.get_close_words(word, 1)
                # correct it to a word if it has > 50% of occurences
                total_counts = sum(c for w, c in close_words) 
                for close_word, count in close_words:
                    if (close_word != word and self.in_dict(close_word)
                            and count/total_counts >= 0.5):
                        rules[word] = close_word
                        break
                    print(word, close_words, file=save_file)
        print('\nRules', file=save_file)
        rules_table = PrettyTable(['Word', 'Correction'])
        for w, c in rules.items():
            rules_table.add_row([w, c])
        print(rules_table, file=save_file)
        return rules


if __name__ == '__main__':
    args = parser.parse_args()
    dataset, dataset_corrections = DigitizationParser().parse_digitization(
            args.dataset)
    dataset_words = []
    for essay in dataset:
        sents = sent_tokenize(essay)
        dataset_words += [w for sent in sents for w in word_tokenize(sent) if
                w.isalpha() and not any([char.isupper() for char in w[1:]])]
    corrector = InteractiveCorrector(
            DistMatrix(dataset_words, damerau_levenshtein_distance))
    corrector.extract_rules(args.save_file)
