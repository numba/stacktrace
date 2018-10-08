from stacktrace.timer import Timer
from stacktrace.utils import simple_processing, skip_python


def base_address(entry):
    return entry.addr - entry.offset



class Profiler(object):
    def __init__(self, tid, **kwargs):
        self._timer = Timer(tid=tid, func=self._handler, **kwargs)
        self._profile = {}

    def get_result(self):
        """Get the raw result as a dict
        """
        return self._profile

    def get_sorted(self):
        return sorted(
            self._profile.items(),
            key=lambda x: x[1]['count'],
            reverse=True,
            )

    def _handler(self, rawtrace):
        # NOTE: always skip python entries for now
        for entry in skip_python(simple_processing(rawtrace)):
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
        self._timer.start()

    def join(self):
        self._timer.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, excvalue, tb):
        self.join()

