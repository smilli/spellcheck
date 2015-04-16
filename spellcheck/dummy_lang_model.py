from pylm.lang_model import LanguageModel

class DummyLanguageModel(LanguageModel):

    def __init__(self):
        pass

    def order(self):
        return 1

    def prob(self, word, context):
        return 0
