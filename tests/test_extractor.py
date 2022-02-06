import os
from os.path import join, dirname, abspath
from typing import List

from hiword import extract_keywords


def _load_docs() -> List[str]:
    docs = []
    base_dir = join(dirname(abspath(__file__)), 'docs')
    for i in os.listdir(base_dir):
        if i.endswith('.txt'):
            with open(join(base_dir, i), 'r') as f:
                docs.append(f.read())
    return docs


def test_extract_keywords():
    docs = _load_docs()
    for i, s in enumerate(docs):
        print('#{}: {}'.format(i + 1, s))
        print('#keywords:')
        for x, w in extract_keywords(s, with_weight=True):
            print(x, w)
