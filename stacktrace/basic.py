from __future__ import print_function

import ctypes
import sys
import threading

from . import core
from .utils import simple_processing, skip_python
from io import StringIO


def _identity(x):
    return x


def _get_local_stack(size, maxdepth):
    buf = ctypes.create_string_buffer(size)
    outsz = core.backtrace_local(buf, size, maxdepth)
    rawtrace = buf[:outsz].decode('ascii')
    return rawtrace


def print_stack(file=sys.stdout, size=1024 * 4, maxdepth=100,
                show_python=True):
    rawtrace = _get_local_stack(size=size, maxdepth=maxdepth)
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


def get_thread_stack(tid, show_python=True):
    """Get the stacktrace for a given thread.

    Parameters
    ----------
    tid : int
        The thread-id of the thread to be traced.  It can be the current
        thread.
    show_python : bool; optional
        Set to *True* (default) to keep the Python entries in the returned
        stacktrace.

    Returns
    -------
    stacktrace : list
        A list of ``stack.utils.StackEntry``
    """
    if tid == threading.get_ident():
        size = 1024 * 4
        maxdepth = 100
        rawtrace = _get_local_stack(size=size, maxdepth=maxdepth)
    else:
        def handler(buf, outsz):
            rawtrace = buf[:outsz].decode()
            rawlog.append(rawtrace)

        rawlog = []
        cb = core.bt_callback(handler)
        core.backtrace_thread(tid, cb)
        rawtrace = rawlog.pop()

    # Process
    pyprocess = _identity if show_python else skip_python
    processed = pyprocess(simple_processing(rawtrace))
    return list(processed)

