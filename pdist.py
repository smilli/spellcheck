from collections import defaultdict
from functools import reduce
from operator import mul

class ProbDist:
    """Probability distribution."""

    def __init__(self, counts, total_counts=None, default_func=None):
        """
        Construct ProbDist.

        Params:
            counts: [dict{string, int}] Dict from edit to number of counts
                for the edit.  This is used to estimate P(edit|spelling error).
            total_counts: [int] Total number of counts in data.  Supply to avoid
                computation of the sum of all counts if data is large.
            default_func: [function] A function that returns a probability for
                items that were never seen in training data.
        """
        total_counts = sum(c for i, c in counts.items())
        self.probs = defaultdict(default_func or (lambda: 1/total_counts))
        for e, c in counts.items():
            self.probs[e] = c/total_counts

    def prob(self, item):
        return self.probs[item]

def parse_counts(file_name, sep='\t', encoding=None):
    """
    Parse frequency counts from file.

    Params:
        file_name: [string] The path to the file to parse.  File should have
            lines formatted as <item><sep><count>.  For example: "e|i   917"
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
