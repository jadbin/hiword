# coding=utf-8

from os import listdir
from os.path import join, dirname, isdir
from multiprocessing import Lock

default_dict = {}
dict_loader_lock = Lock()

default_idf = {}
idf_loader_lock = Lock()

default_stopwords = set()
stopwords_loader_lock = Lock()


class DictLoader:
    def __init__(self, file=None):
        self.dict = self._load_dict(file)

    def word_freq(self, word):
        if word in self.dict:
            return self.dict[word][0]
        return 0

    def word_pos(self, word):
        if word in self.dict:
            return self.dict[word][1]
        return None

    @staticmethod
    def _load_dict(dict_file):
        def read_dict():
            with open(dict_file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    s = line.split()
                    res[s[0]] = (int(s[1]), s[2])

        if dict_file is None:
            with dict_loader_lock:
                if len(default_dict) > 0:
                    return default_dict
                dict_file = join(dirname(__file__), 'data', 'dict.txt')
                res = default_dict
                read_dict()
        else:
            res = {}
            read_dict()
        return res


class IDFLoader:
    def __init__(self, file=None):
        self.idf = self._load_idf(file)
        self.median_idf = sorted(self.idf.values())[len(self.idf) // 2]

    def word_idf(self, word):
        return self.idf.get(word, self.median_idf)

    @staticmethod
    def _load_idf(idf_file):
        def read_idf():
            with open(idf_file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    s = line.split()
                    res[s[0]] = float(s[1])

        if idf_file is None:
            with idf_loader_lock:
                if len(default_idf) > 0:
                    return default_idf
                idf_file = join(dirname(__file__), 'data', 'idf.txt')
                res = default_idf
                read_idf()
        else:
            res = {}
            read_idf()
        return res


class StopwordsLoader:
    def __init__(self, file=None):
        self.stopwords = self._load_stopwords(file)

    def is_stopword(self, word):
        return word in self.stopwords

    @staticmethod
    def _load_stopwords(file):
        def read_stopwords():
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

        if file is None:
            with stopwords_loader_lock:
                if len(default_stopwords) > 0:
                    return default_stopwords
                file = join(dirname(__file__), 'data', 'stopwords')
                res = default_stopwords
                read_stopwords()
        else:
            res = set()
            read_stopwords()
        return res
