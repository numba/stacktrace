import threading
import os

import numpy as np
from numba import njit

from stacktrace.core import get_thread_id
from stacktrace.timer import Timer
from stacktrace.utils import simple_processing, skip_python

print(os.getpid())


@njit(nogil=True)
def foo():
    out = 0
    for j in range(1000):
        x = np.arange(100).astype(np.float32)
        out += np.cos(x).sum() * np.linalg.norm(x)

    return out


def other_thread():
    print('actual tid', get_thread_id())
    print("STARTED")
    for i in range(500):
        foo()
    print("ENDED")


th = threading.Thread(target=other_thread)
th.start()
tid = th.ident
print('tid', tid)


def bt_handler(rawtrace):
    print("STACK:", len(rawtrace))
    for entry in skip_python(simple_processing(rawtrace)):
        print(entry)


# with Timer(tid, bt_handler, interval=1/20):
with Timer(tid, bt_handler, interval=1/1000):
    print("TIMER STARTED")
    th.join()
    print("THREAD JOIN")
