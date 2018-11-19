from __future__ import division

import threading
import time

from stacktrace.basic import DEFAULT_MAXDEPTH, get_thread_stack
from stacktrace._docutils import apply_doc



class Timer(object):
    """A Timer object that repeatedly invoke backtrace on a target thread
    at a given frequency.
    """
    @apply_doc
    def __init__(self, tid, func, interval=1/20,
                 maxdepth=DEFAULT_MAXDEPTH, show_python=True):
        """
        Parameters
        ----------
        tid : int
            Target thread id.
        func : callable
            A callback function that takes a single argument.
            A list of *StackEntries* will be passed in.
            It will be called upon every stacktrace with the trace info
            as a string.
        interval : float
            Sampling frequency in seconds.  Default to 1/20 (i.e. 20Hz).
            The value is passed to `time.sleep()`.
        {doc_maxdepth}
        {doc_show_python}

        Example
        -------

        Use as context-manager:

            with Timer(tid, print):
                code_to_be_traced()

        Use with explicit .start() and .join():

            timer = Timer(tid, print)
            timer.start()
            code_to_be_traced()
            timer.join()
        """
        self._tid = tid
        self._interval = interval
        self._func = func
        self._cont = True
        self._maxdepth = maxdepth
        self._show_python = show_python
        self._thread = threading.Thread(target=self._handle_on_time)

    def start(self):
        """Start the timer.
        """
        self._thread.start()

    def join(self):
        """Stop and wait for the timer-thread to end.
        """
        self._cont = False
        self._thread.join()

    def _handle_on_time(self):
        """The private callback from the timer.
        """
        while self._cont:
            stack_entries = get_thread_stack(
                tid=self._tid,
                maxdepth=self._maxdepth,
                show_python=self._show_python,
            )
            self._func(stack_entries)
            time.sleep(self._interval)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, excvalue, tb):
        self.join()
