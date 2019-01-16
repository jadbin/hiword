# coding=utf-8

import math
from collections import defaultdict

from jieba import Tokenizer

from hiword.dataloader import DictLoader, IDFLoader

__all__ = ['KeywordsExtractor', 'extract_keywords']


class KeywordsExtractor:
    NUMERIC = '0123456789〇一二三四五六七八九十百千万亿元角分'

    def __init__(self, topk=20, min_support=2, dict_file=None, idf_file=None):
        self.tokenizer = Tokenizer()
        self.topk = topk
        self.min_support = min_support
        self.dict = DictLoader(dict_file)
        self.idf = IDFLoader(idf_file)

    def extract_keywords(self, *docs, topn=20, with_weight=False):
        freq = defaultdict(lambda: 0)
        doc_freq = defaultdict(lambda: 0)
        for d in docs:
            if isinstance(d, str):
                words = []
                for i in self.tokenizer.cut(d):
                    w = i.strip()
                    if len(w) == 0:
                        continue
                    words.append(w)
            else:
                words = d
            keywords = self._extract_keywords_from_single_doc(words)
            seg = self._detect_long_keywords(words, keywords)
            f = defaultdict(lambda: 0)
            for w in seg:
                if self._filter_word(w):
                    continue
                f[w] = f[w] + 1
            for k, v in f.items():
                doc_freq[k] = doc_freq[k] + 1
                freq[k] = freq[k] + v
        res = []
        for k in freq:
            s = freq[k] / (freq[k] + self.dict.word_freq(k))
            s *= math.log2(freq[k] + 1) * math.log2(doc_freq[k] + 1)
            s *= math.log2(1 + len(docs) / doc_freq[k])
            res.append((k, s))
        res.sort(key=lambda x: x[1], reverse=True)
        res = res[:topn]
        if with_weight:
            return res
        return [i[0] for i in res]

    def _detect_long_keywords(self, words, keywords):
        if not isinstance(keywords, set):
            keywords = set(keywords)
        appears = defaultdict(lambda: 0)
        ran = []
        w = []

        def commit():
            i = 0
            for i in range(len(w), 0, -1):
                if self.dict.word_pos(w[i - 1]) not in ('v',):
                    break
            if i > 0:
                word = ''.join(w[:i])
                appears[word] += 1
                ran.append((cur - i, cur, word))

        for cur in range(0, len(words)):
            x = words[cur]
            if x in keywords:
                w.append(x)
            elif w:
                commit()
                w = []
        if w:
            commit()

        seg = []
        last = 0
        for begin, end, word in ran:
            if begin > last:
                for i in range(last, begin):
                    seg.append(words[i])
            if appears[word] < self.min_support:
                for i in range(begin, end):
                    seg.append(words[i])
            else:
                seg.append(word)
        for i in range(last, len(words)):
            seg.append(words[i])
        return seg

    def _extract_keywords_from_single_doc(self, words):
        freq = {}
        for w in words:
            if len(w) < 2:
                continue
            freq[w] = freq.get(w, 0.0) + 1.0
        total = sum(freq.values())
        for k in freq:
            freq[k] *= self.idf.word_idf(k) / total
        keywords = sorted(freq, key=freq.__getitem__, reverse=True)
        return keywords[:self.topk]

    def _filter_word(self, w):
        def isnumber(v):
            if v:
                v = v.strip('%')
            try:
                v = float(v)
            except ValueError:
                return False
            return True

        if isnumber(w):
            return True
        if len(w) <= 1:
            return True
        nc = 0
        for i in w:
            if i in self.NUMERIC:
                nc += 1
        if nc * 2 >= len(w):
            return True
        return False


def extract_keywords(*docs, topn=20, with_weight=False, **kwargs):
    extractor = KeywordsExtractor(**kwargs)
    return extractor.extract_keywords(*docs, topn=topn, with_weight=with_weight)
