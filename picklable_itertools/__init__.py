import collections
import os.path
import sys

from pkg_resources import get_distribution, DistributionNotFound

from .base import BaseItertool
from .iter_dispatch import (
    _iter, ordered_sequence_iterator, file_iterator, range_iterator
    )


try:
    DIST = get_distribution('picklable_itertools')
    DIST_LOC = os.path.normcase(DIST.location)
    HERE = os.path.normcase(__file__)
    if not HERE.startswith(os.path.join(DIST_LOC, 'picklable_itertools')):
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'not installed'
else:
    __version__ = DIST.version


class repeat(BaseItertool):
    """
    repeat(object [,times]) -> create an iterator which returns the object
    for the specified number of times.  If not specified, returns the object
    endlessly.
    """
    def __init__(self, obj, times=None):
        self._obj = obj
        self._times = times
        self._times_called = 0

    def __next__(self):
        if self._times is None:
            return self._obj
        else:
            if self._times > self._times_called:
                self._times_called += 1
                return self._obj
            else:
                raise StopIteration


class chain(BaseItertool):
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


class compress(BaseItertool):
    """compress(data, selectors) --> iterator over selected data

    Return data elements corresponding to true selector elements.
    Forms a shorter iterator from selected data elements using the
    selectors to choose the data elements.
    """
    def __init__(self, data, selectors):
        self._data = _iter(data)
        self._selectors = _iter(selectors)

    def __next__(self):
        # We terminate on the shortest input sequence, so leave
        # StopIteration uncaught here.
        data = next(self._data)
        selector = next(self._selectors)
        while not bool(selector):
            data = next(self._data)
            selector = next(self._selectors)
        return data


class count(BaseItertool):
    """count(start=0, step=1) --> count object

    Return a count object whose .__next__() method returns consecutive values.
    """
    def __init__(self, start=0, step=1):
        self._n = start
        self._step = step

    def __next__(self):
        n = self._n
        self._n += self._step
        return n


class cycle(BaseItertool):
    """cycle(iterable) --> cycle object

    Return elements from the iterable until it is exhausted.
    Then repeat the sequence indefinitely.
    """
    def __init__(self, iterable):
        self._iterable = _iter(iterable)
        self._exhausted = False
        self._elements = collections.deque()

    def __next__(self):
        if not self._exhausted:
            try:
                value = next(self._iterable)
            except StopIteration:
                self._exhausted = True
                return next(self)
            self._elements.append(value)
        else:
            if len(self._elements) == 0:
                raise StopIteration
            value = self._elements.popleft()
            self._elements.append(value)
        return value


class imap(BaseItertool):
    """imap(func, *iterables) --> imap object

    Make an iterator that computes the function using arguments from
    each of the iterables.  Stops when the shortest iterable is exhausted.
    """
    def __init__(self, function, *iterables):
        self._function = function
        self._iterables = tuple([_iter(it) for it in iterables])

    def __next__(self):
        args = tuple([next(it) for it in self._iterables])
        if self._function is None:
            return args
        else:
            return self._function(*args)


def izip(*iterables):
    """zip(iter1 [,iter2 [...]]) --> zip object

    Return a zip object whose .__next__() method returns a tuple where
    the i-th element comes from the i-th iterable argument.  The .__next__()
    method continues until the shortest iterable in the argument sequence
    is exhausted and then it raises StopIteration.
    """
    return imap(None, *iterables)


class ifilter(BaseItertool):
    """ifilter(function or None, iterable) --> ifilter object

    Return an iterator yielding those items of iterable for which function(item)
    is true. If function is None, return the items that are true.
    """
    def __init__(self, predicate, iterable):
        self._predicate = predicate if predicate is not None else bool
        self._iterable = _iter(iterable)

    def __next__(self):
        val = next(self._iterable)
        print("val", val)
        while not self._predicate(val):
            val = next(self._iterable)
            print("val", val)
        return val


class ifilterfalse(ifilter):
    """ifilterfalse(function or None, sequence) --> ifilterfalse object

    Return those items of sequence for which function(item) is false.
    If function is None, return the items that are false.
    """
    def __init__(self, predicate, iterable):
        super(ifilterfalse, self).__init__(predicate, iterable)
        self._true_predicate = self._predicate
        self._predicate = self._negated

    def _negated(self, argument):
        return not self._true_predicate(argument)


class zip_longest(BaseItertool):
    def __init__(self, *iterables, **kwargs):
        if 'fillvalue' in kwargs:
            self._fillvalue = kwargs['fillvalue']
            del kwargs['fillvalue']
        else:
            self._fillvalue = None
        if len(kwargs) > 0:
            raise ValueError("Unrecognized keyword arguments: {}".format(
                ", ".join(kwargs)))

        self._iterables = [_iter(it) for it in iterables]

    def __next__(self):
        found_any = False
        result = []
        for it in self._iterables:
            try:
                result.append(next(it))
                found_any = True
            except StopIteration:
                result.append(self._fillvalue)
        if found_any:
            return tuple(result)
        else:
            raise StopIteration


class islice(BaseItertool):
    def __init__(self, iterable, start, stop=None, step=1):
        if stop is None:
            start, stop = 0, start
        if (not 0 <= start <= sys.maxsize or
                not 0 <= stop <= sys.maxsize or
                not 0 <= step <= sys.maxsize):
            raise ValueError("Indices for islice() must be None or an "
                             "integer: 0 <= x <= maxint.")

        self._iterable = _iter(iterable)
        i = 0
        while i < start:
            try:
                next(self._iterable)
                i += 1
            except StopIteration:
                break

        self._stop = stop - start
        self._step = step
        self._n = 0

    def __next__(self):
        while self._n % self._step and self._n < self._stop:
            next(self._iterable)
            self._n += 1
        if self._n == self._stop:
            raise StopIteration
        value = next(self._iterable)
        self._n += 1
        return value
