from collections import namedtuple


class StackEntry(namedtuple("StackEntry", "addr,name,offset")):
    def __str__(self):
        if self.offset:
            offset = ' +{}'.format(self.offset)
        else:
            offset = ''
        return '[0x{:x}] {}{}'.format(self.addr, self.name, offset)




def split(rawtrace):
    lines = rawtrace.splitlines()
    for ln in lines:
        addr, more = ln.split(':', 1)
        where = more.rfind('+')
        if where < 0:
            fname = more
            offset = 0
        else:
            fname, offset = more.rsplit('+')
            offset = int(offset, 16)
        entry = StackEntry(int(addr, 16), fname, offset)
        yield entry


_sure_python_names = {
    '_PyEval_EvalFrameDefault',
    '_PyEval_EvalCodeWithName',
    'PyObject_Call',
    '_PyObject_FastCallDict',
    '_PyObject_FastCallDict',
    'PyCFuncPtr_call',
}


_maybe_python_names = {
    'function_call',
    'fast_function',
    'call_function',
    'method_call',
    'slot_tp_call',
    'builtin_exec',
    'partial_call',
} | _sure_python_names


def is_python_stack_sure(entry):
    return entry.name in _sure_python_names


def is_python_stack_maybe(entry):
    return any([entry.name in _maybe_python_names,
                entry.name.startswith('Py'),
                entry.name.startswith('_Py')])


def simple_processing(rawtrace):
    for i, entry in enumerate(split(rawtrace)):
        if i == 0 and entry.name == '_bt_callback':
            continue
        elif i == 1 and entry.name == '_sigtramp':
            continue
        else:
            yield entry


def skip_python(entry_iter):
    last_is_py = False
    skipped = []

    def show_skipped():
        repl = '<skipped {} Python entries>'.format(len(skipped))
        first = skipped[0]
        del skipped[:]
        return entry._replace(
            addr=first.addr,
            name=repl,
            offset=0,
            )


    for entry in entry_iter:
        if skip_python:
            if last_is_py:
                if is_python_stack_maybe(entry):
                    skipped.append(entry)
                    continue
                else:
                    if skipped:
                        yield show_skipped()
                    last_is_py = False
                    yield entry
            elif is_python_stack_sure(entry):
                    last_is_py = True
        yield entry
    else:
        if skipped:
            yield show_skipped()