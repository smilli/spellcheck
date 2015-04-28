from spellcheck.spellchecker import SpellChecker, SpellingCorrection

class CombinedSpellChecker(SpellChecker):

    def __init__(self, spellcheckers):
        """
        Construct CombinedSpellChecker.

        Params:
            spellcheckers: [list] Spellcheckers in order of descending priority.
        """
        self.spellcheckers = spellcheckers

    def spellcheck(self, dataset):
        sc_corrections = [sc.spellcheck(dataset) for sc in self.spellcheckers]
        final_corrections = []
        for _ in range(len(dataset)):
            final_corrections.append([])
        corrections_set = set()
        for sc_correction in sc_corrections:
            for essay_ind, essay_corrections in enumerate(sc_correction):
                for correction in essay_corrections:
                    key = (essay_ind, correction.index, correction.word)
                    if key not in corrections_set:
                        corrections_set.add(key)
                        final_corrections[essay_ind].append(correction)
        return final_corrections
