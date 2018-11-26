import os
import ctypes

# Detect on RTD
on_rtd = os.environ.get('READTHEDOCS') == 'True'
try:
    from . import _bt
except ImportError:
    # Change C-extension behavior on readthedocs
    if not on_rtd:
        # Re-raise if not on RTD
        raise
    else:
        # Import mock module
        from . import _bt_mock as _bt


bt_callback = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_size_t)


def _wrap_fnptr(ptr, restype, *argtypes):
    proto = ctypes.CFUNCTYPE(restype, *argtypes)
    return proto(ptr)


backtrace_local = _wrap_fnptr(
    _bt.backtrace_local,
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
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
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
if not on_rtd:
    initialize_thread()
