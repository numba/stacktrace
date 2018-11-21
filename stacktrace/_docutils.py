
import re
from functools import lru_cache
from textwrap import dedent, indent


doc_file = """
file : fileobj
    The file object to print to.  Defaults to ``sys.stdout``.
""".strip()

doc_maxdepth = """
maxdepth : int
    Maximum stack depth.
""".strip()

doc_show_python = """
show_python : bool
    Whether to filter out python stack entries.
""".strip()

doc_common_kwargs = {
    'doc_file': doc_file,
    'doc_maxdepth': doc_maxdepth,
    'doc_show_python': doc_show_python,
}


_regex_whitespace = re.compile(r'\s+')

def _find_indent(text):
    for ln in text.splitlines():
        m = _regex_whitespace.match(ln)
        if m:
            return len(m.group(0))
    return 0


@lru_cache(4)
def _get_indented(depth):
    return {k: indent(v, ' ' * depth, lambda ln: ln[0] == ' ')
            for k, v in doc_common_kwargs.items()}


def apply_doc(fn):
    olddoc = fn.__doc__
    depth = _find_indent(olddoc)
    what = _get_indented(depth)
    newdoc = dedent(olddoc).format(**what)
    fn.__doc__ = newdoc
    return fn
