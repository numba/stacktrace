import ctypes
from . import _bt


bt_callback = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_size_t)


def _wrap_fnptr(ptr, restype, *argtypes):
    proto = ctypes.CFUNCTYPE(restype, *argtypes)
    return proto(ptr)


backtrace = _wrap_fnptr(
    _bt.backtrace,
    # return type
    ctypes.c_size_t,
    # arg types
    ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
)


backtrace_thread = _wrap_fnptr(
    _bt.backtrace_thread,
    # return type
    ctypes.c_int,
    # arg types
    ctypes.c_void_p, ctypes.c_void_p,
)


get_thread_id = _wrap_fnptr(
    _bt.get_thread_id,
    # return type
    ctypes.c_void_p,
    # arg types
)


initialize_thread = _wrap_fnptr(
    _bt.initialize_thread,
    # return type
    None,
    # arg types
)

# Initialize
initialize_thread()
