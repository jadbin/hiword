import os
from collections import defaultdict
from os import listdir
from os.path import join, dirname, isdir


class DictLoader:
    def __init__(self):
        self.dict = self._load_dict()

    def word_freq(self, word):
        return self.dict[word]

    @staticmethod
    def _load_dict():
        res = defaultdict(lambda: 0)
        d = join(dirname(__file__), 'data', 'dicts')
        for name in os.listdir(d):
            if name.endswith('.txt'):
                dict_file = join(d, name)
                with open(dict_file) as f:
                    for line in f:
                        s = line.split()
                        res[s[0]] = max(res[s[0]], int(s[1]))
        return res


class IDFLoader:
    def __init__(self):
        self.idf = self._load_idf()
        self.median_idf = sorted(self.idf.values())[len(self.idf) // 2]

    def word_idf(self, word):
        return self.idf.get(word, self.median_idf)

    @staticmethod
    def _load_idf():
        idf_file = join(dirname(__file__), 'data', 'idf.txt')
        res = {}
        with open(idf_file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                s = line.split()
                res[s[0]] = float(s[1])
        return res


class StopwordsLoader:
    def __init__(self):
        self.stopwords = self._load_stopwords()

    def is_stopword(self, word):
        return word in self.stopwords

    def remove(self, word):
        self.stopwords.remove(word)

    @staticmethod
    def _load_stopwords():
        file = join(dirname(__file__), 'data', 'stopwords')
        res = set()
        files = []
        if isdir(file):
            for fname in listdir(file):
                if fname.endswith('.txt'):
                    files.append(join(file, fname))
        else:
            files.append(file)
        for fname in files:
            with open(fname) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    s = line.strip()
                    res.add(s)
        return res
