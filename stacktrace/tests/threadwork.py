import re
import string
import random


def get_thread_work_func():

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

    return other_thread
