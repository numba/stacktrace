import os
from distutils.core import setup, Extension


# Detect conda prefix
conda_prefix = os.environ.get('CONDA_PREFIX', '')
conda_include_path = os.path.join(conda_prefix, 'include')
conda_lib_path = os.path.join(conda_prefix, 'lib')
print('conda_include_path={}'.format(conda_include_path))
print('conda_lib_path={}'.format(conda_lib_path))

module_bt = Extension(
    'stacktrace._bt',
    sources=['stacktrace/bt.c'],
    include_dirs=[conda_include_path],
    library_dirs=[conda_lib_path],
    libraries=['unwind'],
    )

with open('README.md') as fin:
    readmetext = fin.read()


setup(
    name='stacktrace',
    version='0.1',
    description='Low-level stacktraces in Python',
    author='Siu Kwan Lam',
    long_description=readmetext,
    packages=[
        'stacktrace',
        'stacktrace.tools',
        'stacktrace.tests',
        ],
    ext_modules=[module_bt],
)
