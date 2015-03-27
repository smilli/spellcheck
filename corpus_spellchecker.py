from edit_dist_spellchecker import EditDistanceSpellChecker
from pdist import ProbDist
from collections import Counter
import nltk

class CorpusSpellChecker(EditDistanceSpellChecker):

    def __init__(self, dataset, edit_pdist, corpus_names=None):
        """
        Construct CorpusSpellChecker.

        Params:
            dataset: [list of strings] The essays to correct.
            edit_pdist: [EditProbDist obj] An estimated probability distribution
                for types of edits.
            corpus_names: [list of strings] Names of NLTK corpora to use.
                Ex: ['gutenberg', 'brown'] Default is to use only Gutenberg.
        """
        if not corpus_names:
            corpus_names = ['gutenberg']
        corpora = []
        for corpus_name in corpus_names:
            try:
                corpus = getattr(nltk.corpus, corpus_name)
            except AttributeError:
                raise Exception('You must provide a valid corpus name')
            corpora.append(corpus)
        counts = Counter(w.lower() for corpus in corpora for w in
                corpus.words())
        word_pdist = ProbDist(counts)
        super().__init__(dataset, edit_pdist, word_pdist)
