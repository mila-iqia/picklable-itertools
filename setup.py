"""Installation script."""
from os import path
from setuptools import find_packages, setup

from picklable_itertools.version import __version__

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md')) as f:
    LONG_DESCRIPTION = f.read().strip()

setup(
    name='picklable-itertools',
    version=__version__,
    description='itertools. But picklable.',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/dwf/picklable_itertools',
    author='David Wade-Farley',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities'
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='pickle serialize pickling itertools iterable iteration',
    packages=find_packages(exclude=['tests']),
    install_requires=['six'])
