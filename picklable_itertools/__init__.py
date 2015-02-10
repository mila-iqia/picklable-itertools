import six
import collections


def _iter(obj):
    """A custom replacement for iter(), dispatching a few custom picklable
    iterators for known types.
    """
    if six.PY2 and isinstance(obj, (list, tuple)):
        return ordered_sequence_iterator(obj)
    else:
        return iter(obj)


class ordered_sequence_iterator(six.Iterator):
    """A picklable replacement for list and tuple iterators."""
    def __init__(self, sequence):
        self._sequence = sequence
        self._position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._position < len(self._sequence):
            return self._sequence[self._position]
        else:
            raise StopIteration


class repeat(six.Iterator):
    """
    repeat(object [,times]) -> create an iterator which returns the object
    for the specified number of times.  If not specified, returns the object
    endlessly.
    """
    def __init__(self, obj, times=None):
        self._obj = obj
        self._times = times
        self._times_called = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._times is None:
            return self._obj
        else:
            if self._times > self._times_called:
                self._times_called += 1
                return self._obj
            else:
                raise StopIteration


class chain(six.Iterator):
    """
    chain(*iterables) --> chain object

    Return a chain object whose .__next__() method returns elements from the
    first iterable until it is exhausted, then elements from the next
    iterable, until all of the iterables are exhausted.
    """
    def __init__(self, *iterables):
        self._iterables = collections.deque(iterables)
        self._current = repeat(None, 0)

    def __next__(self):
        try:
            return next(self._current)
        except StopIteration:
            try:
                self._current = _iter(self._iterables.popleft())
            except IndexError:
                raise StopIteration
        return next(self)
