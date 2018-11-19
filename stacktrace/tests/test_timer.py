import threading

from stacktrace.tools import Timer
from stacktrace.utils import StackEntry
from .threadwork import get_thread_work_func


def test_timer():
    th = threading.Thread(target=get_thread_work_func())
    th.start()
    tid = th.ident

    stack_data = []

    def bt_handler(entries):
        stack_data.append(entries)

    with Timer(tid, bt_handler, interval=1/1000, show_python=False):
        th.join()

    assert isinstance(stack_data[0], list)
    print('len(stack_data)', len(stack_data))
    assert len(stack_data) > 10
    non_empty_traces = [stack for stack in stack_data if len(stack) > 0]
    print('len(non_empty_traces)', len(non_empty_traces))
    assert len(non_empty_traces) > 10
    # check that the traces are well-formed
    for stack in non_empty_traces:
        assert all(isinstance(x, StackEntry) for x in stack)

