from . import Timer


def base_address(entry):
    return entry.addr - entry.offset


class Profiler(object):
    """This classs wraps the ``stacktrace.tools.Timer`` for providing profiling
    data by processing the stack traces, grouping them and counting their
    occurances.  The data is stored as a dictionary that can be retrieved by
    using ``.get_result()`` or ``.get_sorted()``.

    Parameters
    ----------
    tid : int
        Target thread id.
    **kwargs :
        Other keywords arguments to ``stacktrace.tools.Timer``.

    Examples
    --------

    Use as context-manager:

    >>> with Profiler(tid) as prof:
    ... code_to_be_traced()
    >>> stacktraces = prof.get_result()

    Use with explicit ``.start()`` and ``.join()``:

    >>> prof = Profiler(tid)
    >>> prof.start()
    >>> code_to_be_traced()
    >>> prof.join()
    >>> stacktraces = prof.get_result()
    """
    def __init__(self, tid, **kwargs):
        """

        """
        self._timer = Timer(tid=tid, func=self._handler, **kwargs)
        self._profile = {}

    def get_result(self):
        """Get the stacktrace result as a dict.

        Example
        -------

        Sample data:

            {4317941904: {'count': 3, 'name': 'method_get'},
             4318042736: {'count': 1, 'name': 'frame_dealloc'},
             4318048880: {'count': 1, 'name': 'PyFrame_New'},
             4318056128: {'count': 1, 'name': 'PyFunction_NewWithQualName'}}

        The first level keys are the symbol address.  The first level values
        are the *count* that the symbol has appeared on the stack.  The *name*
        is the name of the symbol, which can be a '?' for unknown symbol
        (because of lack of debug information).
        """
        return self._profile

    def get_sorted(self):
        """Get results sorted by *count*.

        Returns
        -------

        sorted_entries : list
            List of 2-tuples, which are in the same format of
            ``self.get_result().items()``.

        """
        return sorted(
            self._profile.items(),
            key=lambda x: x[1]['count'],
            reverse=True,
            )

    def _handler(self, entries):
        for entry in entries:
            if entry.is_python:
                continue
            base = base_address(entry)
            if base not in self._profile:
                d = {'count': 0, 'name': entry.name}
            else:
                d = self._profile[base]

            d['count'] += 1
            self._profile[base] = d

    def start(self):
        """Start the profiler
        """
        self._timer.start()

    def join(self):
        """Stop the profiler
        """
        self._timer.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, excvalue, tb):
        self.join()

