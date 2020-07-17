# coding=utf-8

from os.path import join, dirname
from multiprocessing import Lock

zh_hans = {}
zh_hans_lock = Lock()


def traditional_to_simple(text):
    with zh_hans_lock:
        if len(zh_hans) == 0:
            file = join(dirname(__file__), 'data', 'zh_hans.txt')
            with open(file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    s = line.split()
                    zh_hans[s[0]] = s[1]

    res = []
    for i in text:
        if i in zh_hans:
            res.append(zh_hans[i])
        else:
            res.append(i)
    return ''.join(res)
