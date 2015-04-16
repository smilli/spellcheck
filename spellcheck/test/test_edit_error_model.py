import unittest
from collections import defaultdict
from spellcheck.edit_error_model import EditErrorModel

class TestEditErrorModel(unittest.TestCase):

    def test_edit_error_model(self):
        edit_pdist = defaultdict(int, {'e|i': 0.5, 's|st': 0.2, 'ai|a': 0.3})
        prob_spelling_error = 0.01
        error_model = EditErrorModel(edit_pdist,
                prob_spelling_error=prob_spelling_error)
        for edit, prob in edit_pdist.items():
            self.assertEqual(error_model.prob(edit), prob * prob_spelling_error)
        self.assertEqual(error_model.prob(''), 1 - prob_spelling_error)
        self.assertEqual(error_model.prob('e|i+s|st'), 0.1 * prob_spelling_error)
        self.assertEqual(error_model.prob('s|st+e|i'), 0.1 *
                prob_spelling_error)
        self.assertEqual(error_model.prob('s|st+e|i+ai|a'), 0.03 *
                prob_spelling_error)


if __name__ == '__main__':
    unittest.main()
