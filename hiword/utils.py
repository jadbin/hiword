from multiprocessing import Lock
from os.path import join, dirname

_zh_hans = {}
_zh_hans_lock = Lock()


def _load():
    file = join(dirname(__file__), 'data', 'zh_hans.txt')
    with open(file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            s = line.split()
            _zh_hans[ord(s[0])] = ord(s[1])


def traditional_to_simple(text: str):
    with _zh_hans_lock:
        if len(_zh_hans) == 0:
            _load()

    return text.translate(_zh_hans)
