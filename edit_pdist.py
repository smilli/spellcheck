from collections import defaultdict
from functools import reduce
from operator import mul

class EditProbDist:
    """Estimated probability distribution for edits."""

    def __init__(self, counts, prob_spelling_error=0.05, default_func=None):
        """
        Construct EditProbDist.

        Params:
            counts: [dict{string, int}] Dict from edit to number of counts
                for the edit.  This is used to estimate P(edit|spelling error).
            prob_spelling_error: [float] The probability that a spelling error
                occurs in text.
            default_func: [function] A function that returns a probability for
                validly formatted edits that were never seen in training data.
        """
        edit_counts = counts.items()
        total_counts = sum(c for e, c in edit_counts)
        self.prob_spelling_error = prob_spelling_error
        self.probs = defaultdict(default_func or (lambda: 1/total_counts))
        for e, c in edit_counts:
            self.probs[e] = c/total_counts

    def valid_edit(self, edit):
        # TODO(smilli)
        return True

    def prob(self, edit):
        if self.valid_edit(edit):
            prob_edit_given_error = reduce(
                mul, (self.probs[edit] for edit in edit.split('+')))
            if edit == '':
                return (1 - self.prob_spelling_error) * prob_edit_given_error
            else:
                return self.prob_spelling_error * prob_edit_given_error
        raise InvalidEditException()

class InvalidEditException(Exception):
    pass

def parse_edit_pdist(file_name, sep='\t', encoding=None):
    """
    Parse EditProbDist from of file with lines of form edit count.

    Params:
        file_name: [string] The path to the file to parse.  File should have
            lines formatted as <edit><sep><count>.  For example: "e|i   917"
        sep: [string] The separator between fields on a line.
        encoding: [string] Type of encoding to use.  Ex: 'utf-8'
    Returns:
        counts: [dict{string, int}] Dict from edit to number of counts
            for the edit.
    """
    counts = {}
    with open(file_name, encoding=encoding) as f:
        for line in f:
            edit, count = line.split(sep)
            counts[edit] = int(count)
    return counts
