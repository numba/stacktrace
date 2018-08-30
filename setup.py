from distutils.core import setup, Extension


module_bt = Extension('stacktrace._bt', sources=['stacktrace/bt.c'])

with open('README.md') as fin:
    readmetext = fin.read()


setup(
    name='stacktrace',
    version='0.1',
    description='Low-level stacktraces in Python',
    author='Siu Kwan Lam',
    long_description=readmetext,
    ext_modules=[module_bt],
)
