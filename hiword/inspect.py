# coding=utf-8

from hiword.dataloader import IDFLoader, StopwordsLoader

_stopwords = None


def is_stopword(word: str):
    global _stopwords
    if _stopwords is None:
        _stopwords = StopwordsLoader()
    return _stopwords.is_stopword(word)


_idf = None


def word_idf(word: str):
    global _idf
    if _idf is None:
        _idf = IDFLoader()
    return _idf.word_idf(word)
