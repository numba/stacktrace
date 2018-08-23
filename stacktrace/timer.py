from __future__ import division
import threading
import time
from stacktrace.core import backtrace_thread, get_thread_id, bt_callback


class Timer(object):
    """A Timer object that repeatedly invoke backtrace on a target thread
    at a given frequency.
    """
    def __init__(self, tid, func, interval=1/20):
        """
        Parameters
        ----------
        tid : int
            Target thread id.
        func : callable
            A callback function with signature `(str) -> None`.
            It will be called upon every stacktrace with the trace info
            as a string.
        internval : float
            Sampling frequency in seconds.  Default to 1/20 (i.e. 20Hz).
            The value is passed to `time.sleep()`.

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
        self._cb = bt_callback(self._handle_backtrace)
        self._func = func
        self._cont = True
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

    def _handle_backtrace(self, buffer, size):
        """The private callback from the backtrace function that parses the
        raw C-buffer and keeps the timer going.
        """
        decoded = buffer[:size].decode()
        self._func(decoded)

    def _handle_on_time(self):
        """The private callback from the timer.
        """
        while self._cont:
            self._cont = backtrace_thread(self._tid, self._cb)
            time.sleep(self._interval)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, excvalue, tb):
        self.join()
