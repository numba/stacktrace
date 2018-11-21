# StackTrace

[![Build Status](https://travis-ci.org/numba/stacktrace.svg?branch=master)](https://travis-ci.org/numba/stacktrace)

Provide facility to obtain low-level stacktraces from within Python.

This project relies on *libunwind*, which works on Unix-like and OSX system.

## Features

* Access to C stack backtrace inside Python.
    * Useful for debugging code that interleave native code and Python code.
* Access to C stack of another thread in the same process.
    * Useful for debugging multi-threaded programs.


## Getting the dependencies

For development, *libunwind* must be available. The simplest way is to get
*libunwind* using conda:

```bash
conda install -c defaults -c conda-forge libunwind
```

# Install

Once you have the dependencies, you can run `python setup.py install` to
install into your python package directory.
