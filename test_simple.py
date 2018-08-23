from stacktrace.core import backtrace

import ctypes


size = 1024 * 4
buf = ctypes.create_string_buffer(size)
print(ctypes.sizeof(buf))
outsz = backtrace(buf, size, 100)
print(outsz)
for ln in buf[:outsz].decode('ascii').split('\n'):
    print(ln)