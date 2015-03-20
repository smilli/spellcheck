from spellchecker import SpellingCorrection
import re

class Parser:

    def __init__(self, end_of_essay='# # # # # # #'):
        self.end_of_essay = end_of_essay

    def _split(self, seq, sep):
        chunk = []
        for el in seq:
            if el == sep:
                yield chunk
                chunk = []
            else:
                chunk.append(el)
        yield chunk

    def _split_string(self, string, sep):
        return [''.join(x) for x in self._split(string, sep)]

    def _parse_correction(self, essay_metadata):
        """
        Parse SpellingCorrection objects out of essay metadata.

        essay_metadata: [array of strings] first element is essay number,
            second is the essay text, and any elements after that are spelling
            corrections
        """
        corrections = []
        for correction in essay_metadata[2:]:
            index, word, correction = list(self._split_string(correction, ','))
            index = int(index)
            corrections.append(SpellingCorrection(index, word, [correction]))
        return corrections

    def parse_digitization(self, file_name):
        """
        Parse essay text and SpellingCorrection objs out of each digitization.
        """
        essays = []
        corrections = []
        with open(file_name) as data_file:
            lines = data_file.read().splitlines()
            essays_with_metadata = list(self._split(lines, self.end_of_essay))
            essays = []
            essay_corrections = []
            for e in essays_with_metadata[:-1]:
                essay_text = re.sub(r'<([^>]*)>', r'\1', e[1])
                essays.append(essay_text)
                essay_corrections.append(self._parse_correction(e))
        return essays, essay_corrections
