.. stacktrace documentation master file, created by
   sphinx-quickstart on Wed Nov 21 11:40:49 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to stacktrace's documentation!
======================================

Provide facility to obtain low-level stacktraces from within Python.

This project relies on *libunwind*, which works on Unix-like and OSX system.

Features
--------

* Access to C stack backtrace inside Python.
    * Useful for debugging code that interleave native code and Python code.
* Access to C stack of another thread in the same process.
    * Useful for debugging multi-threaded programs.


Getting the dependencies
------------------------

For development, *libunwind* must be available. The simplest way is to get
*libunwind* using conda:

.. code-block:: bash

   conda install -c defaults -c conda-forge libunwind


Install
-------

Once you have the dependencies, you can run `python setup.py install` to
install into your python package directory.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   basic.rst
   tools.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
