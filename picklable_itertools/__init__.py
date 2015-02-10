import six
import collections


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
                self._current = iter(self._iterables.popleft())
            except IndexError:
                raise StopIteration
        return next(self)
