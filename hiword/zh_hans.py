# coding=utf-8

from multiprocessing import Lock
from os.path import join, dirname

zh_hans = {}
zh_hans_lock = Lock()


def traditional_to_simple(text: str):
    with zh_hans_lock:
        if len(zh_hans) == 0:
            file = join(dirname(__file__), 'data', 'zh_hans.txt')
            with open(file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    s = line.split()
                    zh_hans[ord(s[0])] = ord(s[1])

    return text.translate(zh_hans)
