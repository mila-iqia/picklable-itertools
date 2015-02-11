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
    if isinstance(obj, file_types):
        return file_iterator(obj)
    else:
        return iter(obj)


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
