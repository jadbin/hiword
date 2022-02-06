import re
from multiprocessing import Lock
from os.path import join, dirname

_zh_hans = {}
_zh_hans_lock = Lock()


def _load_zh_hans():
    file = join(dirname(__file__), 'data', 'zh_hans.txt')
    with open(file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            s = line.split()
            _zh_hans[ord(s[0])] = ord(s[1])


def traditional_to_simple(text: str) -> str:
    with _zh_hans_lock:
        if len(_zh_hans) == 0:
            _load_zh_hans()

    return text.translate(_zh_hans)


_invalid_chars_reg = re.compile(
    r'[^' +
    r'a-zA-Z0-9' +
    r',.!?()@&_\-' +
    r'\u4e00-\u9fa5' +
    r'\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b' +
    r']'
)


def filter_invalid_chars(text: str, char: str = None) -> str:
    if not char:
        char = ' '
    return _invalid_chars_reg.sub(char, text)
