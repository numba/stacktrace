from io import StringIO
import re

import pytest

from stacktrace import print_stack

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


@pytest.mark.parametrize('size', [0, 10, 50, 100])
def test_print_stack_with_size(size):
    with StringIO() as buf:
        print_stack(file=buf, size=size)
        output = buf.getvalue()
    assert len(output) <= size
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
