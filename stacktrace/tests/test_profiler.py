import threading

from stacktrace.tools import Profiler
from .threadwork import get_thread_work_func


def test_profiler():
    th = threading.Thread(target=get_thread_work_func())
    th.start()
    tid = th.ident

    with Profiler(tid, interval=1/1000, show_python=False) as prof:
        th.join()

    # Check get_result
    pdata = prof.get_result()

    assert isinstance(pdata, dict)
    # enough symbols
    assert len(pdata) > 10
    firstkey, firstvalue = next(iter(pdata.items()))
    assert isinstance(firstkey, int)
    assert firstvalue['count'] > 0
    assert isinstance(firstvalue['name'], str)
    assert firstvalue['name']

    # Check .get_sorted
    sorted_data = prof.get_sorted()
    assert isinstance(sorted_data, list)
    assert len(sorted_data) == len(pdata)
    # Check ordering
    last = sorted_data[0][1]['count']
    for k, v in sorted_data[1:]:
        assert v['count'] <= last
        last = v['count']
