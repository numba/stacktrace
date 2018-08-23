// The file is setup as a Python C-extension for convenience.
// Nothing in the functionality really requires to be a C-extension.
// The functions defined in this file is exported as function pointers
// directly.  The python-side just acess them as ctypes.

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <setjmp.h>
#include <pthread.h>
#define UNW_LOCAL_ONLY
#include <libunwind.h>

#include <Python.h>


#if PY_MAJOR_VERSION >= 3
  #define MOD_ERROR_VAL NULL
  #define MOD_SUCCESS_VAL(val) val
  #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
  #define MOD_DEF(ob, name, doc, methods) { \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef); }
  #define MOD_INIT_EXEC(name) PyInit_##name();
#else
  #define MOD_ERROR_VAL
  #define MOD_SUCCESS_VAL(val)
  #define MOD_INIT(name) PyMODINIT_FUNC init##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
  #define MOD_INIT_EXEC(name) init##name();
#endif

static jmp_buf jbuf;

static
void _bt_signal_handler(int signo)
{
    siglongjmp(jbuf, 1);
}

/*
This function is adapted from Eli Berdensky's blogpost:
https://eli.thegreenplace.net/2015/programmatic-access-to-the-call-stack-in-c/
Modified to to print data to a buffer.
*/
size_t backtrace(char *out_records, size_t out_record_size,
                 int maxcount)
{
  unw_cursor_t cursor;
  unw_context_t context;
  char *bufptr = out_records;
  char sym[129];
  size_t remaining = out_record_size;

  // setup signal handler in case that's a signal due to error within the
  // backtrace code, so we will abort the backtrace and return to user code
  // without interruption.
  signal(SIGILL, _bt_signal_handler);
  signal(SIGSEGV, _bt_signal_handler);
  // Initialize cursor to current frame for local unwinding.
  unw_getcontext(&context);
  unw_init_local(&cursor, &context);

  if ( sigsetjmp(jbuf, !0) == 0) {
    // Unwind frames one by one, going up the frame stack.
    for (int ct = 0; ct < maxcount && unw_step(&cursor) > 0; ++ct) {
      unw_word_t offset, pc;
      unw_get_reg(&cursor, UNW_REG_IP, &pc);
      if (pc == 0) {
        break;
      }

      size_t used = 0;
      if (unw_get_proc_name(&cursor, sym, sizeof(sym) - 1, &offset) == 0) {
          used = snprintf(bufptr, remaining,
                          "%p:%s+%p\n", (void*)pc, sym, (void*)offset);
      } else {
          used = snprintf(bufptr, remaining, "0x%llx: ?\n", pc);
      }
      remaining -= used;
      bufptr += used;
    }
  }

  return bufptr - out_records;
}

// ---------------------------------------------------------------------------
// The interface below are for getting backtraces from threads.
// To use these functionality, initialize_thread() must be called to
// initialize the subsystem.

void* get_thread_id() {
  return pthread_self();
}


#define SIG_STACKTRACE SIGUSR2

static int _initialized = 0;

struct {
  pthread_mutex_t mutex;
  char *out_records;
  size_t out_record_size;
  int maxdepth;
  size_t record_written;
  pthread_t calling_thread;
  volatile int spinlock;
} TheSignalConfig;


static char _default_buffer[1024 * 100];

static
void _finalize_thread() {
  pthread_mutex_destroy(&TheSignalConfig.mutex);
}

/*
Non-threadsafe.  Must be called before backtrace_thread() is used.
Can be invoked multiple times.
*/
void initialize_thread() {
  if (_initialized) return;
  _initialized = 1;

  pthread_mutex_init(&TheSignalConfig.mutex, NULL);
  TheSignalConfig.out_records = _default_buffer;
  TheSignalConfig.out_record_size = sizeof(_default_buffer);
  TheSignalConfig.maxdepth = 1000;

  // Register finalization function
  atexit(_finalize_thread);
}

void _setup_signal_handler(void* callback, struct sigaction *old_sa){
  struct sigaction sa;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = SA_SIGINFO;
  sa.sa_sigaction = callback;
  sigaction(SIG_STACKTRACE, &sa, old_sa);
}

static
int _send_signal_to_thread(void *tid) {
  return pthread_kill((pthread_t)tid, SIG_STACKTRACE) == 0;
}

static
void _bt_callback() {
  if (TheSignalConfig.calling_thread == get_thread_id()) {
    return;
  }
  TheSignalConfig.record_written = backtrace(
    TheSignalConfig.out_records,
    TheSignalConfig.out_record_size,
    TheSignalConfig.maxdepth
    );
  // signal the caller
  TheSignalConfig.spinlock = 1;
}

static
void _wait_and_reset_signal(struct sigaction *old_sa) {
  // spin and wait.
  while (TheSignalConfig.spinlock == 0);
  // reset signal handlers
  sigaction(SIG_STACKTRACE, old_sa, NULL);
}

typedef int callback_type(const char* buf, size_t bufsz);
/*
Signal a thread by thread-id (i.e pthread_t) and causes it to run the
backtrace function.  Save and return the result.

Returns
  1: success
  0: fail
*/
int backtrace_thread(void* tid, callback_type *cb){
  // Pre-check
  void* this_thread = get_thread_id();
  // disallow calling on the same thread
  if (this_thread == tid) {
    return 0;
  }
  // Critical section
  pthread_mutex_lock(&TheSignalConfig.mutex);
  TheSignalConfig.spinlock = 0;
  TheSignalConfig.calling_thread = this_thread;

  struct sigaction oldsa;
  _setup_signal_handler(_bt_callback, &oldsa);

  int retcode = 0;
  if ( _send_signal_to_thread(tid) ) {
    // Wait for signal handler to complete in the target-thread
    _wait_and_reset_signal(&oldsa);
    // Invoke callback
    cb(TheSignalConfig.out_records,
      TheSignalConfig.out_record_size);

    retcode = 1;  // OK
  }
  pthread_mutex_unlock(&TheSignalConfig.mutex);
  return retcode;
}


// ------------------------------------------------------------------------
// Code to pretend this is a Python C-extension.

static PyMethodDef ext_methods[] = {};

MOD_INIT(_bt) {
    PyObject *m;
    MOD_DEF(m, "_bt", "No docs", ext_methods)
    if (m == NULL) return MOD_ERROR_VAL;

    #define DECLPOINTER(Fn) PyModule_AddObject(m, #Fn, PyLong_FromVoidPtr(&Fn))
    DECLPOINTER(backtrace_thread);
    DECLPOINTER(initialize_thread);
    DECLPOINTER(get_thread_id);
    DECLPOINTER(backtrace);
    #undef DECLPOINTER
    return MOD_SUCCESS_VAL(m);
}
