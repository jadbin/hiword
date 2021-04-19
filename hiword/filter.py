from abc import abstractmethod, ABCMeta


class WordFilter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, word: str) -> bool:
        pass


class WordFilterChain(WordFilter):
    def __init__(self, *word_filters: WordFilter):
        super().__init__()
        self.word_filters = list(word_filters)

    def filter(self, word: str) -> bool:
        for f in self.word_filters:
            if f.filter(word):
                return True
        return False


class NumericFilter(WordFilter):
    NUMERIC = set('0123456789〇一二三四五六七八九十百千万亿元角分')

    def filter(self, word: str):
        if self._is_number(word):
            return True
        nc = 0
        for i in word:
            if i in self.NUMERIC:
                nc += 1
        if nc * 2 >= len(word):
            return True
        return False

    def _is_number(self, v):
        if v:
            v = v.strip('%')
        try:
            v = float(v)
        except ValueError:
            return False
        return True
