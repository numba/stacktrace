from __future__ import print_function

import ctypes
import sys
import threading
from io import StringIO

from . import core
from .utils import simple_processing, skip_python
from ._docutils import apply_doc


DEFAULT_MAXDEPTH = 100
DEFAULT_BUFSIZE = 4 * 1024


def _identity(x):
    return x


def _get_local_stack(bufsize, maxdepth):
    """Wraps the low-level API to get a backtrace of the current thread.
    Performs minimal processing to return a string buffer.
    """
    buf = ctypes.create_string_buffer(bufsize)
    outsz = core.backtrace_local(buf, bufsize, maxdepth)
    rawtrace = buf[:outsz].decode('ascii')
    return rawtrace


@apply_doc
def print_stack(file=sys.stdout, maxdepth=DEFAULT_MAXDEPTH,
                show_python=True, _bufsize=DEFAULT_BUFSIZE):
    """Print the stack of the current thread.

    Parameters
    ----------
    {doc_file}
    {doc_maxdepth}
    {doc_show_python}
    """
    rawtrace = _get_local_stack(bufsize=_bufsize, maxdepth=maxdepth)
    pyprocess = _identity if show_python else skip_python
    for entry in pyprocess(simple_processing(rawtrace)):
        print(entry, file=file)


def print_thread_stack(tid, file=sys.stdout, maxdepth=DEFAULT_MAXDEPTH,
                       show_python=True):
    """Print the stack of the target thread

    Parameters
    ----------
    tid : int
        The target thread-id.
    {doc_file}
    {doc_maxdepth}
    {doc_show_python}
    """
    entries = get_thread_stack(
        tid=tid,
        maxdepth=maxdepth,
        show_python=show_python,
        )
    for entry in entries:
        print(entry, file=file)


def get_thread_stack(tid, maxdepth=DEFAULT_MAXDEPTH, show_python=True):
    """Get the stack of the target thread

    Parameters
    ----------
    tid : int
        The target thread-id.
    {doc_file}
    {doc_maxdepth}
    {doc_show_python}

    Returns
    -------
    stacktrace : list
        A list of namedtuples ``(addr, name, offset, is_python)``
    """
    if tid == threading.get_ident():
        bufsize = DEFAULT_BUFSIZE
        maxdepth = maxdepth
        rawtrace = _get_local_stack(bufsize=bufsize, maxdepth=maxdepth)
    else:
        def handler(buf, outsz):
            rawtrace = buf[:outsz].decode()
            rawlog.append(rawtrace)

        rawlog = []
        cb = core.bt_callback(handler)
        core.backtrace_thread(tid, cb, maxdepth)
        rawtrace = rawlog.pop()

    # Process
    pyprocess = _identity if show_python else skip_python
    processed = pyprocess(simple_processing(rawtrace))
    return list(processed)
