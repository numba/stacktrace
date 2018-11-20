import re
import time
import threading
from io import StringIO
from contextlib import contextmanager

import pytest

from stacktrace import (
    print_stack,
    print_thread_stack,
)


def verify_stack_buffer(output):
    assert len(output) > 0
    lines = output.splitlines()
    assert len(lines) > 0

    pat = re.compile(r'\[0x[0-9a-z]+\]\s+[_a-zA-Z0-9]+\s+\+\d+')
    for ln in lines:
        assert pat.match(ln)


def test_print_stack():
    with StringIO() as buf:
        print_stack(file=buf)
        output = buf.getvalue()
    verify_stack_buffer(output)


@pytest.mark.parametrize('bufsize', [0, 10, 50, 100])
def test_print_stack_with_bufsize(bufsize):
    with StringIO() as buf:
        print_stack(file=buf, _bufsize=bufsize)
        output = buf.getvalue()
    assert len(output) <= bufsize
    if len(output) > 0:
        verify_stack_buffer(output)


@pytest.mark.parametrize('maxdepth', [0, 13, 29])
def test_print_stack_with_maxdepth(maxdepth):
    with StringIO() as buf:
        print_stack(file=buf, maxdepth=maxdepth)
        output = buf.getvalue()
    assert len(output.splitlines()) <= maxdepth
    if maxdepth > 0:
        verify_stack_buffer(output)


@contextmanager
def make_temp_thread():
    def inner():
        time.sleep(0.001)
    def run():
        inner()
    thread = threading.Thread(target=run)
    thread.start()
    yield thread.ident
    thread.join()


def test_print_thread_stack():
    with make_temp_thread() as tid:
        with StringIO() as buf:
            print_thread_stack(tid=tid, file=buf)
            output = buf.getvalue()
    if output:
        verify_stack_buffer(output)


@pytest.mark.parametrize('maxdepth', [0, 13, 29])
def test_print_thread_stack_with_maxdepth(maxdepth):
    with make_temp_thread() as tid:
        with StringIO() as buf:
            print_thread_stack(tid, file=buf, maxdepth=maxdepth)
            output = buf.getvalue()
    if output and maxdepth > 0:
        assert len(output.splitlines()) <= maxdepth
        verify_stack_buffer(output)
