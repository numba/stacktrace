from __future__ import print_function

import ctypes
import sys

from . import core
from .utils import simple_processing, skip_python


def _identity(x):
    return x


def print_stack(file=sys.stdout, size=1024 * 4, maxdepth=100,
                show_python=True):
    buf = ctypes.create_string_buffer(size)
    outsz = core.backtrace(buf, size, maxdepth)
    rawtrace = buf[:outsz].decode('ascii')
    pyprocess = _identity if show_python else skip_python
    for entry in pyprocess(simple_processing(rawtrace)):
        print(entry, file=file)


def print_thread_stack(tid, file=sys.stdout, show_python=True):
    def handler(buf, outsz):
        rawtrace = buf[:outsz].decode('ascii')
        pyprocess = _identity if show_python else skip_python
        for entry in pyprocess(simple_processing(rawtrace)):
            print(entry, file=file)

    cb = core.bt_callback(handler)
    core.backtrace_thread(tid, cb)
