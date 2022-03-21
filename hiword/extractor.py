import math
from collections import defaultdict
from typing import Dict, List, Union

from LAC import LAC

from hiword.dataloader import DictLoader, IDFLoader, StopwordsLoader
from hiword.filter import WordFilterChain, NumericFilter
from hiword.utils import traditional_to_simple, filter_invalid_chars


class KeywordsExtractor:
    MIN_WORD_FREQ = 3

    def __init__(self):
        self.lac = LAC(mode='seg')
        self.dict = DictLoader()
        self.idf = IDFLoader()
        self.stopwords = StopwordsLoader()

        self.word_filter = WordFilterChain(
            NumericFilter(),
        )

    def extract_keywords(self, doc):
        words = self._tokenize(doc)
        keywords = self._extract_short_keywords(words)
        long_words = self._detect_long_keywords(words, keywords)

        freq = defaultdict(lambda: 0)
        for word, count in keywords.items():
            if self.word_filter.filter(word):
                continue
            freq[word] += count
        for word, count in long_words.items():
            if self.word_filter.filter(word):
                continue
            freq[word] += count

        res = self._rerank_words(freq)
        res = self._filter_subwords(res, freq)

        # FIXME: 根据经验设置的权重阈值
        min_weight = 0.1
        res = [[k, v] for k, v in res if v >= min_weight]
        return res

    def _tokenize(self, doc: Union[str, List[str]]) -> List[str]:
        if isinstance(doc, str):
            words = []
            for i in self.lac.run(doc):
                w = i.strip()
                if len(w) == 0:
                    continue
                words.append(w)
        else:
            words = doc
        return words

    def _filter_subwords(self, words: list, freq: Dict[str, int]) -> list:
        merged = []
        for i in range(len(words)):
            w1 = words[i][0]
            w1_ok = True
            for j in range(len(words)):
                w2 = words[j][0]
                if len(w1) < len(w2) and w1 in w2 and freq[w1] == freq[w2]:
                    w1_ok = False
                    break
            if w1_ok:
                merged.append([w1, words[i][1]])
        return merged

    def _detect_long_keywords(self, words: list, short_words: dict) -> dict:
        appears = {}

        a = []
        for w in words:
            if w in short_words:
                a.append(w)
            elif a:
                self._commit_continuous_words(a, appears)
                a = []
        if a:
            self._commit_continuous_words(a, appears)

        long_words = {}
        for word, count in appears.items():
            if count >= self.MIN_WORD_FREQ:
                long_words[word] = count
        return long_words

    def _commit_continuous_words(self, continuous_words: list, appears: dict):
        end_pos = len(continuous_words)
        if end_pos > 0:
            for i in range(0, end_pos - 1):
                for j in range(i + 2, end_pos + 1):
                    word = ''.join(continuous_words[i:j])
                    if word in appears:
                        appears[word] += 1
                    else:
                        appears[word] = 1

    def _extract_short_keywords(self, words) -> dict:
        freq = {}
        for w in words:
            if self.stopwords.is_stopword(w):
                continue
            if w in freq:
                freq[w] += 1
            else:
                freq[w] = 1

        tfidf = {}
        for k in freq:
            tfidf[k] = freq[k] * self.idf.word_idf(k)

        t = []
        for w in tfidf:
            t.append([w, tfidf[w]])
        t.sort(key=lambda x: x[1], reverse=True)

        topk = 500
        # FIXME: 根据文本长度等信息动态调整简单关键词的数量
        result = {}
        for w, _ in t:
            if freq[w] >= self.MIN_WORD_FREQ:
                result[w] = freq[w]
            if len(result) >= topk:
                break
        return result

    def _rerank_words(self, freq: Dict[str, int]) -> list:
        res = []
        for k in freq:
            s = math.log2(freq[k] + 0.5) * (freq[k] / (freq[k] + self.dict.word_freq(k)))
            # FIXME: 融合词汇本身的信息量
            res.append([k, s])
        res.sort(key=lambda x: x[1], reverse=True)
        return res


_keywords_extractor = KeywordsExtractor()


def extract_keywords(doc, with_weight=False):
    # 繁体转简体
    doc = traditional_to_simple(doc)
    # 过滤无效字符
    doc = filter_invalid_chars(doc)
    keywords = _keywords_extractor.extract_keywords(doc)
    if not with_weight:
        keywords = [k[0] for k in keywords]
    return keywords
