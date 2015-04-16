from functools import reduce
from operator import mul

class EditErrorModel():
    """Estimated probability distribution for edits."""

    def __init__(self, edit_pdist, prob_spelling_error=0.01):
        """
        Construct EditProbDist.

        Params:
            edit_pdist: [dict{string, float}] Dict from a single edit to prob
                for the edit.  This is used to estimate P(edit|spelling error).
            prob_spelling_error: [float] The probability that a spelling error
                occurs in text.
        """
        self.edit_pdist = edit_pdist
        self.prob_spelling_error = prob_spelling_error

    def valid_edit(self, edit):
        # TODO(smilli)
        return True

    def prob(self, edit):
        if self.valid_edit(edit):
            prob_edit_given_error = reduce(
                mul, (self.edit_pdist[edit] for edit in edit.split('+')))
            if edit == '':
                return (1 - self.prob_spelling_error)
            else:
                return self.prob_spelling_error * prob_edit_given_error
        raise InvalidEditException()

class InvalidEditException(Exception):
    pass
