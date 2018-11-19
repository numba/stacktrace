import threading
import os
import re
import string
import random

from stacktrace.core import get_thread_id
from stacktrace.tools import Timer
from stacktrace.utils import simple_processing, skip_python, StackEntry


def test_timer():
    def gen(n):
        # Generate some data
        text = [string.ascii_letters for i in range(n)]
        random.shuffle(text)
        return ''.join(text)

    def work():
        pat = re.compile(r'\w+')
        out = []
        for i in range(100):
            data = gen(i)
            m = pat.match(gen(i))
            if m:
                out.append(m.group(0))
        return out


    def other_thread():
        out = []
        for i in range(100):
            out.append(work())

    th = threading.Thread(target=other_thread)
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

