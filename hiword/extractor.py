# coding=utf-8

import math
from collections import defaultdict

from jieba import Tokenizer

from hiword.dataloader import DictLoader, IDFLoader, StopwordsLoader
from hiword.zh_hans import traditional_to_simple

__all__ = ['KeywordsExtractor', 'extract_keywords']


class KeywordsExtractor:
    NUMERIC = '0123456789〇一二三四五六七八九十百千万亿元角分'
    tokenizer = None
    dict = None
    idf = None
    stopwords = None

    def __init__(self):
        cls = self.__class__
        if cls.tokenizer is None:
            cls.tokenizer = Tokenizer()
        if cls.dict is None:
            cls.dict = DictLoader()
        if cls.idf is None:
            cls.idf = IDFLoader()
        if cls.stopwords is None:
            cls.stopwords = StopwordsLoader()

    def extract_keywords(self, doc, with_weight=False):
        if isinstance(doc, str):
            words = []
            for i in self.tokenizer.cut(doc, HMM=False):
                w = i.strip()
                if len(w) == 0:
                    continue
                words.append(w)
        else:
            words = doc
        keywords = self._extract_keywords_from_single_doc(words)
        long_words = self._detect_long_keywords(words, keywords)
        freq = defaultdict(lambda: 0)
        for word, count in keywords:
            if self._filter_word(word):
                continue
            freq[word] += count
        for word, count, p in long_words:
            if self._filter_word(word):
                continue
            freq[word] += count

        res = []
        for k in freq:
            s = freq[k] / (freq[k] + self.dict.word_freq(k))
            s *= math.log2(freq[k] + 0.5)
            # TODO: 融合词汇本身的信息量
            res.append((k, s))
        res.sort(key=lambda x: x[1], reverse=True)

        def post_process():
            n = 0
            while n < len(res):
                # TODO: 合理计算阈值
                if res[n][1] < 0.1:
                    break
                n += 1
            not_merge = res[:n]
            merged = []
            for i in range(len(not_merge)):
                w1 = not_merge[i][0]
                w1_ok = True
                for j in range(len(not_merge)):
                    w2 = not_merge[j][0]
                    if len(w1) < len(w2) and w1 in w2 and freq[w1] == freq[w2]:
                        w1_ok = False
                        break
                if w1_ok:
                    merged.append(not_merge[i])
            return merged

        res = post_process()

        if with_weight:
            return res
        return [i[0] for i in res]

    def _detect_long_keywords(self, words, keywords):
        keywords = set([t[0] for t in keywords])
        appears = defaultdict(lambda: 0)
        parts = defaultdict(list)

        def commit(continuous_words):
            end_pos = len(continuous_words)
            if end_pos > 0:
                for i in range(0, end_pos - 1):
                    for j in range(i + 2, end_pos + 1):
                        word = ''.join(continuous_words[i:j])
                        appears[word] += 1
                        parts[word] = continuous_words[i:j]

        w = []
        for cur in range(0, len(words)):
            x = words[cur]
            if x in keywords:
                w.append(x)
            elif w:
                commit(w)
                w = []
        if w:
            commit(w)

        long_words = []
        for word, count in appears.items():
            # TODO: 合理计算阈值
            if count >= 2:
                long_words.append((word, count, parts[word]))
        return long_words

    def _extract_keywords_from_single_doc(self, words):
        freq = defaultdict(lambda: 0)
        for w in words:
            if self.stopwords.is_stopword(w):
                continue
            freq[w] += 1
        total = sum(freq.values())
        tfidf = {}
        for k in freq:
            tfidf[k] = freq[k] * self.idf.word_idf(k) / total
        keywords = sorted(tfidf, key=tfidf.__getitem__, reverse=True)
        keywords = [(k, freq[k]) for k in keywords]
        topk = 20
        # TODO: 根据文本长度等信息动态调整简单关键词的数量
        return keywords[:topk]

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
        nc = 0
        for i in w:
            if i in self.NUMERIC:
                nc += 1
        if nc * 2 >= len(w):
            return True
        return False


def extract_keywords(doc, with_weight=False):
    extractor = KeywordsExtractor()
    # 繁体转简体
    doc = traditional_to_simple(doc)
    return extractor.extract_keywords(doc, with_weight=with_weight)
