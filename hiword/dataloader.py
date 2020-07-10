# coding=utf-8

from os.path import join, dirname
from multiprocessing import Lock

default_dict = {}
dict_loader_lock = Lock()

default_idf = {}
idf_loader_lock = Lock()


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
