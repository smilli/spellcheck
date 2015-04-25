import unittest
from spellcheck.interactive_corrector import DistMatrix
from pyxdameraulevenshtein import damerau_levenshtein_distance

class TestDistMatrix(unittest.TestCase):

    def setUp(self):
        self.words = [
            'hello', 'ello', 'great', 'walk',
            'bye', 'hell', 'hello', 'but', 'but']
        self.dmatrix = DistMatrix(self.words, damerau_levenshtein_distance)

    def test_pair_to_dist(self):
        self.assertEqual(self.dmatrix.pair_to_dist('hello', 'ello'), 1)
        self.assertEqual(self.dmatrix.pair_to_dist('ello', 'walk'), 3)

    def test_get_words(self):
        self.assertCountEqual(
            self.dmatrix.get_words(),
            set(self.words))

    def test_get_close_words(self):
        self.assertCountEqual(
            self.dmatrix.get_close_words('hello', 1),
            [('hello', 2), ('ello', 1), ('hell', 1)])
        self.assertCountEqual(
            self.dmatrix.get_close_words('bye', 2),
            [('bye', 1), ('but', 2)])

if __name__ == '__main__':
    unittest.main()
