from spellchecker import SpellingCorrection

class Parser:

    def __init__(self, end_of_essay='# # # # # # #'):
        self.end_of_essay = end_of_essay

    def _split(seq, sep):
        chunk = []
        for el in seq:
            if el == sep:
                yield chunk
                chunk = []
            else:
                chunk.append(el)
        yield chunk

    def _parse_correction(essay_metadata):
        """
        Parse SpellingCorrection objects out of essay metadata.

        essay_metadata: [array of string] first element is essay number,
            second is the essay text, and any elements after that are spelling
            corrections
        """
        corrections = []
        for correction in essay_metadata[2:]:
            index, word, correction = list(split(correction, ','))
            corrections.append(SpellingCorrection(index, word, correction))
        return corrections

    def parse_digitization(file_name):
        """
        Parse essay text and SpellingCorrection objs out of each digitization.
        """
        essays = []
        corrections = []
        with open(file_name) as data_file:
            lines = data_file.read().splitlines()
            essays_with_metadata = list(split(lines, self.end_of_essay))
            essays = []
            essay_corrections = []
            for e in essays_with_metadata[:-1]:
                essays.append(e[1])
                essay_corrections.append(self._parse_correction(e))
        return essays, essay_corrections
