"""Support code for implementing `tee`."""
import collections
import six
from picklable_itertools import iter_


class tee_iterator(six.Iterator):
    """An iterator that works in conjunction with a `tee_manager`."""
    def __init__(self, manager):
        self._manager = manager
        self._deque = collections.deque()

    def _append(self, item):
        self._deque.append(item)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self._deque) > 0:
            return self._deque.popleft()
        else:
            self._manager._advance()
            assert len(self._deque) > 0
            return next(self)


class tee_manager(object):
    """An object that manages a base iterator and publishes results to
    one or more client `tee_iterators`.
    """
    def __init__(self, iterable, n=2):
        self._iterable = iter_(iterable)
        self._tee_iterators = tuple(tee_iterator(self) for i in range(n))

    def iterators(self):
        return list(self._tee_iterators)

    def _advance(self):
        """Advance the base iterator, publish to constituent iterators."""
        elem = next(self._iterable)
        for it in self._tee_iterators:
            it._append(elem)


def tee(iterable, n=2):
    """tee(iterable, n=2) --> tuple of n independent iterators."""
    return tee_manager(iter_(iterable), n=n).iterators()
