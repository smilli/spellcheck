import unittest
from spellcheck.cluster_spellchecker import ClusterSpellChecker

class TestClusterSpelllchecker(unittest.TestCase):

    def setUp(self):
        self.spellchecker = ClusterSpellChecker()

    def test_save_suggested_rules(self):
        dataset = ['I walked along a beach.', 'The beach was beautiful.',
            'The beeich was butiful.']
        self.spellchecker.save_suggested_rules(dataset)
        self.assertEqual(self.spellchecker.rules['beeich'], 'beach')
        self.assertEqual(self.spellchecker.rules['butiful'], 'beautiful')

if __name__ == '__main__':
    unittest.main()
