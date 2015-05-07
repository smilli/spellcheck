from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from prettytable import PrettyTable
import enchant
from spellcheck.edit_dist_spellchecker import EditDistanceSpellChecker
from spellcheck.cluster_spellchecker import ClusterSpellChecker
from spellcheck.combined_spellchecker import CombinedSpellChecker
from spellcheck.parse_util import DigitizationParser, parse_counts
from spellcheck.edit_error_model import EditErrorModel
from spellcheck.dummy_lang_model import DummyLanguageModel
from pylm.util import mle_pdist, mle_cpd, ngram_cfd
from pylm.lang_model import NgramModel, InterpolationModel, CachedModel
import argparse
parser = argparse.ArgumentParser(description='Compare Spellcheckers on a '
    'dataset')
parser.add_argument('-d', '--dataset', help='Path to dataset file.',
        required=True)
parser.add_argument('-f', '--save-file', help='Path to file to save stats to.')


def compute_stats(dataset_corrections, spellchecker_corrections):
    """
    Calculate precision and recall.

    Params:
        dataset_corrections: [list of SpellingCorrection objects] The
            SpellCheckers to test
    """
    positives = 0
    true_positives = 0
    false_negatives = 0
    for (dataset_essay_corrections, spellchecker_essay_corrections) in zip(
            dataset_corrections, spellchecker_corrections):
        dataset_essay_corrections = set(dataset_essay_corrections)
        spellchecker_essay_corrections = set(spellchecker_essay_corrections)
        positives += len(spellchecker_essay_corrections)
        true_positives += len(
                dataset_essay_corrections.intersection(
                    spellchecker_essay_corrections))
        false_negatives += len(
                dataset_essay_corrections.difference(
                    spellchecker_essay_corrections))
    if positives == 0:
        return ['N/A', 'N/A']
    return [true_positives/positives,
            true_positives/(true_positives+false_negatives)]


def display_corrections(spellchecker_name, spellchecker_corrections,
        dataset_corrections, save_file=None):
    t = PrettyTable(['Essay #', 'Index', 'Word', 'Correction', 'Correct?'])
    for (essay_ind, essay_corrections) in enumerate(spellchecker_corrections):
        for correction in essay_corrections:
            is_correct = (correction in dataset_corrections[essay_ind])
            t.add_row([essay_ind, correction.index, correction.word,
                correction.best_correction, is_correct])
    print('%s Corrections' % spellchecker_name)
    print(t)
    if save_file:
        with open(save_file, 'a') as f:
            print('%s Corrections' % spellchecker_name, file=f)
            print(t, file=f)


def display_spellchecker_stats(dataset, dataset_corrections, spellcheckers,
        spellchecker_names, save_file=None):
    """
    Display statistics for the performance of different spellcheckers.

    Params:
        dataset: [list of strings] The list of essays.
        dataset_corrections: [list of list of SpellingCorrection objects] The
            correct spelling corrections for each of the essays in dataset.
        spellcheckers: [list of SpellChecker objects] The SpellCheckers to test.
        spellchecker_names: [list of strings] Names to display for
            Spellcheckers.
        save_file: [string] Path to file to save stats to.
    """
    assert(len(spellcheckers) == len(spellchecker_names))
    display_corrections('Golden Standard', dataset_corrections,
            dataset_corrections, save_file)
    stats_t = PrettyTable(['SpellChecker', 'Precision', 'Recall'])
    for spellchecker, spellchecker_name in zip(spellcheckers, spellchecker_names):
        spellchecker_corrections = spellchecker.spellcheck(dataset)
        display_corrections(spellchecker_name, spellchecker_corrections,
            dataset_corrections, save_file)
        next_row = [spellchecker_name] + compute_stats(dataset_corrections,
            spellchecker_corrections)
        stats_t.add_row(next_row)
    print(stats_t)
    if save_file:
        with open(save_file, 'a') as f:
            print(stats_t, file=f)

def get_word_counts_model(word_counts_file):
    word_counts_cfd = {}
    word_counts_cfd[()] = parse_counts(file_name=word_counts_file)
    word_counts_cpd = mle_cpd(word_counts_cfd)
    return NgramModel(word_counts_cpd, 1)

def create_cache_from_dataset(dataset):
    eng_us_dict = enchant.Dict('en_US')
    eng_gb_dict = enchant.Dict('en_GB')
    words = defaultdict(lambda: defaultdict(int))
    for text in dataset:
        for sent in sent_tokenize(text):
            for w in word_tokenize(sent):
                if eng_us_dict.check(w) or eng_gb_dict.check(w):
                    words[()][w] += 1
    return NgramModel(mle_cpd(words), 1)

def corpus_lowercase_sents(corpus):
    for sent in corpus.sents():
        sent = [w.lower() for w in sent]
        yield sent

if __name__ == '__main__':
    args = parser.parse_args()
    dataset, dataset_corrections = DigitizationParser().parse_digitization(
            args.dataset)
    error_model = EditErrorModel(
        mle_pdist(parse_counts(file_name='../edit_counts.txt',
            encoding='ISO-8859-1')), 0.05)
    cache_unigram_model = create_cache_from_dataset(dataset)
    dummy_lang_model = DummyLanguageModel()
    cache_weight = 0.4
    word_counts_model = get_word_counts_model('../word_counts.txt')
    word_counts_cached_model= CachedModel(
        word_counts_model, cache_unigram_model, cache_weight)
    corpus_cpd = mle_cpd(
        ngram_cfd(corpus_lowercase_sents(nltk.corpus.brown), 2))
    corpus_unigram_model = NgramModel(corpus_cpd, 1)
    corpus_bigram_model = NgramModel(corpus_cpd, 2)
    corpus_interpolation_model = InterpolationModel(corpus_cpd, 2, [0.75, 0.25])
    corpus_cached_unigram_model = CachedModel(
        corpus_unigram_model, cache_unigram_model, cache_weight)
    corpus_cached_bigram_model = CachedModel(
        corpus_bigram_model, cache_unigram_model, cache_weight)
    corpus_cached_interpolation_model = CachedModel(
        corpus_interpolation_model, cache_unigram_model, cache_weight)
    edit_cluster_spellchecker = ClusterSpellChecker()
    edit_cluster_spellchecker.save_edit1_rules(dataset)
    suggest_cluster_spellchecker = ClusterSpellChecker()
    suggest_cluster_spellchecker.save_suggested_rules(dataset)
    edit1_wc_spellchecker = EditDistanceSpellChecker(
        error_model, word_counts_model)
    edit_1_brown_sc = EditDistanceSpellChecker(error_model, corpus_unigram_model)
    edit_2_brown_sc = EditDistanceSpellChecker(error_model, corpus_interpolation_model)
    display_spellchecker_stats(dataset, dataset_corrections,
        [
            EditDistanceSpellChecker(error_model, dummy_lang_model),
            edit_cluster_spellchecker,
            suggest_cluster_spellchecker,
            edit1_wc_spellchecker,
            CombinedSpellChecker([edit_cluster_spellchecker, edit1_wc_spellchecker]),
            edit_1_brown_sc,
            CombinedSpellChecker([edit_cluster_spellchecker, edit_1_brown_sc]),
            edit_2_brown_sc,
            CombinedSpellChecker([edit_cluster_spellchecker, edit_2_brown_sc])
        #    EditDistanceSpellChecker(error_model, corpus_bigram_model),
        #    EditDistanceSpellChecker(error_model, word_counts_cached_model),
        #    EditDistanceSpellChecker(error_model, corpus_cached_unigram_model),
        #    EditDistanceSpellChecker(error_model, corpus_cached_bigram_model),
        #    EditDistanceSpellChecker(error_model, corpus_cached_interpolation_model)
        ],
        [
            'Dummy',
            'Edit Cluster',
            'Suggest Cluster',
            '1-gram Word Counts',
            'Cluster + 1-gram Word Counts',
            '1-gram Brown Corpus',
            'Cluster + 1-gram Brown Corpus',
            'Interpolated 2-gram Brown Corpus',
            'Cluster + Interpolated 2-gram Brown Corpus',
        #    '2-gram Brown Corpus',
        #    '1-gram Word Counts Cached',
        #    'Cached 1-gram Brown Corpus',
        #    'Cached 2-gram Brown Corpus',
        #    'Cached Interpolated 2-gram Brown Corpus'
        ], args.save_file)
