from clust import cluster_ngrams, dl_ngram_dist
from pylm.util import ngrams
from nltk import sent_tokenize, word_tokenize
from spellcheck.parse_util import DigitizationParser
import argparse
parser = argparse.ArgumentParser(description='Cluster ngrams in a dataset.')
parser.add_argument('-d', '--dataset', help='Path to dataset file.',
        required=True)
parser.add_argument('-n', '--ngram', help='Order of ngram. Ex: 3 for trigrams.',
        type=int, required=True)

if __name__ == '__main__':
    args = parser.parse_args()
    dataset, dataset_corrections = DigitizationParser().parse_digitization(
            args.dataset)
    dataset_ngrams = []
    for essay in dataset:
        sents = sent_tokenize(essay)
        for sent in sents:
            words = word_tokenize(sent)
            dataset_ngrams += ngrams(words, args.ngram)
    clusters = cluster_ngrams(dataset_ngrams, dl_ngram_dist, max_dist=1,
            method='single')
    for cluster in clusters:
        print(cluster)
        print()
