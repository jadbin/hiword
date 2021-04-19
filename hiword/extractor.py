import math
from collections import defaultdict
from typing import Dict, List, Union

from jieba import Tokenizer

from hiword.dataloader import DictLoader, IDFLoader, StopwordsLoader
from hiword.filter import WordFilterChain, NumericFilter
from hiword.utils import traditional_to_simple


class KeywordsExtractor:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.dict = DictLoader()
        self.idf = IDFLoader()
        self.stopwords = StopwordsLoader()

        self.word_filter = WordFilterChain(
            NumericFilter(),
        )

    def extract_keywords(self, doc):
        words = self._tokenize(doc)
        keywords = self._extract_shot_keywords(words)
        long_words = self._detect_long_keywords(words, keywords)

        freq = defaultdict(lambda: 0)
        for word, count in keywords:
            if self.word_filter.filter(word):
                continue
            freq[word] += count
        for word, count, _ in long_words:
            if self.word_filter.filter(word):
                continue
            freq[word] += count

        res = self._rerank_words(freq)
        res = self._filter_included_words(res, freq)
        return res

    def _tokenize(self, doc: Union[str, List[str]]) -> List[str]:
        if isinstance(doc, str):
            words = []
            for i in self.tokenizer.cut(doc, HMM=False):
                w = i.strip()
                if len(w) == 0:
                    continue
                words.append(w)
        else:
            words = doc
        return words

    def _filter_included_words(self, words: list, freq: Dict[str, int]):
        not_merge = words
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

    def _extract_shot_keywords(self, words) -> list:
        freq = defaultdict(lambda: 0)
        for w in words:
            if self.stopwords.is_stopword(w):
                continue
            freq[w] += 1
        tfidf = {}
        for k in freq:
            tfidf[k] = freq[k] * self.idf.word_idf(k)
        keywords = sorted(tfidf, key=tfidf.__getitem__, reverse=True)
        keywords = [(k, freq[k]) for k in keywords if freq[k] > 1]
        topk = 100
        # TODO: 根据文本长度等信息动态调整简单关键词的数量
        return keywords[:topk]

    def _rerank_words(self, freq: Dict[str, int]) -> list:
        res = []
        for k in freq:
            s = math.log2(freq[k] + 0.5) * (freq[k] / (freq[k] + self.dict.word_freq(k)))
            # TODO: 融合词汇本身的信息量
            res.append((k, s))
        res.sort(key=lambda x: x[1], reverse=True)
        return res


_keywords_extractor = None


def extract_keywords(doc, with_weight=False):
    global _keywords_extractor
    if _keywords_extractor is None:
        _keywords_extractor = KeywordsExtractor()
    # 繁体转简体
    doc = traditional_to_simple(doc)
    keywords = _keywords_extractor.extract_keywords(doc)
    keywords = [k if with_weight else k[0] for k in keywords if k[1] >= 0.1]
    return keywords
