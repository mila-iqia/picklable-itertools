from .base import BaseItertool
from .iter_dispatch import _iter


class _grouper(BaseItertool):
    def __init__(self, iterator, value, keyfunc):
        self._iterator = iterator
        self._value = value
        self._keyfunc = keyfunc
        self._key = self._keyfunc(self._value)
        self._initialized = False
        self._stream_ended = False
        self._done = False

    def __next__(self):
        if not self._initialized:
            self._initialized = True
            return self._value
        else:
            if self._done:
                raise StopIteration
            try:
                value = next(self._iterator)
            except StopIteration:
                self._stream_ended = True
                self._done = True
                raise
            if self._keyfunc(value) != self._key:
                self._terminal_value = value
                self._done = True
                raise StopIteration
            return value


class groupby(BaseItertool):
    """groupby(iterable[, keyfunc]) -> create an iterator which returns
    (key, sub-iterator) grouped by each value of key(value).
    """
    def __init__(self, iterable, key=None):
        self._key = key
        self._iterable = _iter(iterable)
        self._current_key = self._initial_key = object()

    def _keyfunc(self, value):
        if self._key is None:
            return value
        else:
            return self._key(value)

    def __next__(self):
        if not hasattr(self, '_current_grouper'):
            value = next(self._iterable)
            self._current_grouper = _grouper(self._iterable, value,
                                             self._keyfunc)
            return self._keyfunc(value), self._current_grouper
        else:
            while True:
                try:
                    next(self._current_grouper)
                except StopIteration:
                    break
            if self._current_grouper._stream_ended:
                raise StopIteration
            value = self._current_grouper._terminal_value
            self._current_grouper = _grouper(self._iterable, value,
                                             self._keyfunc)
            return self._keyfunc(value), self._current_grouper
