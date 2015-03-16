from prettytable import PrettyTable

def corrections_to_dict(corrections):
    for essay_corrections in corrections:
        for (i, correction) in essay_corrections:
            correct_corrections[(c.word, i, c.index)] = c.corrections[0]

def display_spellchecker_stats(spellcheckers, dataset_corrections):
    """
    Display statistics for the performance of different spellcheckers.

    Params:
        spellcheckers: [list of SpellChecker objects] the SpellCheckers to test.
        dataset: [list of strings] the list of the essays to correct.
        dataset_corrections: [list of SpellingCorrection objects] the correct
            spelling corrections.
    """
    correct_corrections = corrections_to_dict(dataset_corrections)
    header_row = []
    first_row = []
    for essay_corrections in dataset_corrections:
        for (i, correction) in essay_corrections:
            header_row.append((c.word, i, c.index))
            first_row.append(c.corrections[0])
    t = PrettyTable(header_row)
    t.add_row(first_row)

    for spellchecker in spellcheckers:
        computed_corrections = spellchecker.spellcheck()
        computed_corrections_dict = corrections_to_dict(computed_corrections)
        new_row = []
        for key in header_row:
            if key in computed_corrections_dict:
                new_row.append(computed_corrections_dict[key])
            else:
                new_row.append('-')
        t.add_row(new_row)
    print(t)
