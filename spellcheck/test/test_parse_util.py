import unittest
from nltk import sent_tokenize
from spellcheck.parse_util import word_tokenize

class TestWordTokenize(unittest.TestCase):

    def test_word_tokenize(self):
        text = ('I like cats.  My favorite color is orange.  I always wear a'
               ' sweater.')
        sents = sent_tokenize(text)
        words = [w for sent in sents for w in word_tokenize(sent)]
        self.assertEqual(words,
            ['I', 'like', 'cats', 'My', 'favorite', 'color', 'is', 'orange',
             'I', 'always', 'wear', 'a', 'sweater'])

if __name__ == '__main__':
    unittest.main()

