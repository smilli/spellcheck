import unittest
from collections import defaultdict
from spellcheck.edit_dist_spellchecker import EditDistanceSpellChecker
from spellcheck.edit_error_model import EditErrorModel
from pylm.lang_model import NgramModel
from pylm.util import ngram_cfd, mle_cpd

class TestEditDistanceSpellchecker(unittest.TestCase):

    def setUp(self):
        sentences = [['I', 'like', 'Python', '.']]
        ngram_cpd = mle_cpd(ngram_cfd(sentences, 2))
        lang_model = NgramModel(ngram_cpd, 2)
        edit_pdist = defaultdict(int, {'u|o': 0.5, 'k|ke': 0.2, 'ai|a': 0.3})
        prob_spelling_error = 0.01
        error_model = EditErrorModel(edit_pdist,
                prob_spelling_error=prob_spelling_error)
        self.spellchecker = EditDistanceSpellChecker(error_model, lang_model)

    def test_get_candidates(self):
        pass

    def test_score_correction(self):
        score = self.spellchecker.score_correction(('Python', 'u|o'), ['like'])
        self.assertEqual(score, self.spellchecker.error_model.prob('u|o') *
                self.spellchecker.lang_model.prob('Python', ('like',)))

    def test_spellcheck(self):
        dataset = ['I lik Python']
        corrections = self.spellchecker.spellcheck(dataset)
        self.assertEqual(len(corrections), 1)
        correction = corrections[0][0]
        self.assertEqual(correction.best_correction, 'like')


if __name__ == '__main__':
    unittest.main()
