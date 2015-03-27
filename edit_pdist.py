from pdist import ProbDist
from collections import defaultdict
from functools import reduce
from operator import mul

class EditProbDist(ProbDist):
    """Estimated probability distribution for edits."""

    def __init__(self, counts, prob_spelling_error=0.01, default_func=None):
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
        self.prob_spelling_error = prob_spelling_error
        super().__init__(counts, default_func)

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
