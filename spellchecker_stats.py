from prettytable import PrettyTable

from corpus_spellchecker import CorpusSpellChecker
from digitization_parser import Parser


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
    return [true_positives/positives,
            true_positives/(true_positives+false_negatives)]


def display_corrections(spellchecker_name, spellchecker_corrections):
    print('%s Corrections' % spellchecker_name)
    t = PrettyTable(['Essay #', 'Index', 'Word', 'Correction'])
    for (essay_ind, essay_corrections) in enumerate(spellchecker_corrections):
        for correction in essay_corrections:
            t.add_row([essay_ind, correction.index, correction.word,
                correction.best_correction])
    print(t)


def display_spellchecker_stats(dataset, dataset_corrections, spellcheckers):
    """
    Display statistics for the performance of different spellcheckers.

    Params:
        dataset: [list of strings] The list of the essays to correct.
        dataset_corrections: [list of SpellingCorrection objects] The correct
            spelling corrections for each of the essays in dataset.
        spellcheckers: [list of SpellChecker objects] The SpellCheckers to test.
    """
    display_corrections('Golden Standard', dataset_corrections)
    stats_t = PrettyTable(['SpellChecker', 'Precision', 'Recall'])
    for spellchecker in spellcheckers:
        spellchecker_corrections = spellchecker.spellcheck(dataset)
        display_corrections(str(spellchecker), spellchecker_corrections)
        next_row = [str(spellchecker)] + compute_stats(dataset_corrections,
                spellchecker_corrections)
        stats_t.add_row(next_row)
    print(stats_t)


if __name__ == '__main__':
    dataset, dataset_corrections = (
            Parser().parse_digitization('transcriptions/holiday.txt'))
    display_spellchecker_stats(dataset, dataset_corrections,
            [CorpusSpellChecker('gutenberg')])
