import io

import six
from .base import BaseItertool


def _iter(obj):
    """A custom replacement for iter(), dispatching a few custom picklable
    iterators for known types.
    """
    if six.PY2:
        file_types = file,
    if six.PY3:
        file_types = io.IOBase,

    if six.PY2 and isinstance(obj, (list, tuple)):
        return ordered_sequence_iterator(obj)
    if six.PY2 and isinstance(obj, six.moves.xrange):
        return range_iterator(obj)
    if isinstance(obj, file_types):
        return file_iterator(obj)
    return iter(obj)


class range_iterator(BaseItertool):
    """A picklable range iterator for Python 2"""
    def __init__(self, xrange_):
        self._start, self._stop, self._step = xrange_.__reduce__()[1]
        self._n = self._start

    def __next__(self):
        if (self._step > 0 and self._n < self._stop or
                self._step < 0 and self._n > self._stop):
            value = self._n
            self._n += self._step
            return value
        else:
            raise StopIteration


class file_iterator(BaseItertool):
    """A picklable file iterator."""
    def __init__(self, f):
        self._f = f

    def __next__(self):
        line = self._f.readline()
        if not line:
            raise StopIteration
        return line

    def __getstate__(self):
        name, pos, mode = self._f.name, self._f.tell(), self._f.mode
        return name, pos, mode

    def __setstate__(self, state):
        name, pos, mode = state
        self._f = open(name, mode=mode)
        self._f.seek(pos)


class ordered_sequence_iterator(BaseItertool):
    """A picklable replacement for list and tuple iterators."""
    def __init__(self, sequence):
        self._sequence = sequence
        self._position = 0

    def __next__(self):
        if self._position < len(self._sequence):
            value = self._sequence[self._position]
            self._position += 1
            return value
        else:
            raise StopIteration
