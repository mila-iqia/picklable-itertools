import collections
import os.path
import sys

from pkg_resources import get_distribution, DistributionNotFound

from .base import BaseItertool
from .filter import ifilter, ifilterfalse, dropwhile, takewhile
from .iter_dispatch import (
    _iter, ordered_sequence_iterator, file_iterator, range_iterator
    )
from .tee import tee_manager
_zip = zip
_map = map

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
        self._iterables = _iter(iterables)
        self._current = repeat(None, 0)

    def __next__(self):
        try:
            return next(self._current)
        except StopIteration:
            self._current = _iter(next(self._iterables))
        return next(self)

    @classmethod
    def from_iterable(cls, iterable):
        obj = cls()
        obj._iterables = iterable


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

    def _run(self, args):
        return self._function(*args)

    def __next__(self):
        args = tuple([next(it) for it in self._iterables])
        if self._function is None:
            return args
        else:
            return self._run(args)


class starmap(imap):
    def __init__(self, function, iterable):
        self._iterables = (_iter(iterable),)
        self._function = function

    def _run(self, args):
        return self._function(*args[0])


def izip(*iterables):
    """zip(iter1 [,iter2 [...]]) --> zip object

    Return a zip object whose .__next__() method returns a tuple where
    the i-th element comes from the i-th iterable argument.  The .__next__()
    method continues until the shortest iterable in the argument sequence
    is exhausted and then it raises StopIteration.
    """
    return imap(None, *iterables)


class product(BaseItertool):
    def __init__(self, *args, **kwargs):
        if 'repeat' in kwargs:
            repeat = kwargs['repeat']
            del kwargs['repeat']
        else:
            repeat = None
        if len(kwargs) > 0:
            raise ValueError("Unrecognized keyword arguments: {}".format(
                ", ".join(kwargs)))
        if repeat is not None:
            self._iterables = sum(_zip(*(tee(it, repeat) for it in args)), ())
        else:
            self._iterables = [_iter(it) for it in args]
        self._contents = [[] for it in self._iterables]
        self._exhausted = [False for it in self._iterables]
        self._position = [-1 for it in self._iterables]
        self._initialized = False

    def __next__(self):
        # Welcome to the spaghetti factory.
        def _next(i):
            # Advance the i'th iterator, wrapping if necessary.
            # Returns the next value as well as a "carry bit" that
            # tells us we've wrapped, i.e. to advance iterator i - 1 as well.
            flip = False
            # Handle the case where iteratior i still has stuff in it.
            if not self._exhausted[i]:
                try:
                    value = next(self._iterables[i])
                    self._contents[i].append(value)
                    self._position[i] += 1
                except StopIteration:
                    # If contents is empty, the iterator was empty.
                    if len(self._contents[i]) == 0:
                        raise StopIteration
                    self._exhausted[i] = True
                    self._position[i] = -1  # The recursive call increments.
                    return _next(i)
            else:
                self._position[i] += 1
                self._position[i] %= len(self._contents[i])
                value = self._contents[i][self._position[i]]
                # If we've wrapped, return True for the carry bit.
                if self._position[i] == 0:
                    flip = True
            return value, flip

        # deque is already imported, could append to a list and reverse it.
        result = collections.deque()
        i = len(self._iterables) - 1
        if not self._initialized:
            # On the very first draw we need to draw one from every iterator.
            while i >= 0:
                result.appendleft(_next(i)[0])
                i -= 1
            self._initialized = True
        else:
            # Always advance the least-significant position iterator.
            flip = True
            # Keep drawing from lower-index iterators until the carry bit
            # is unset.
            while flip and i >= 0:
                value, flip = _next(i)
                i -= 1
                result.appendleft(value)
            # If the carry bit is still set after breaking out of the loop
            # above, it means the most-significant iterator has wrapped,
            # and we're done.
            if flip:
                raise StopIteration
            # Read off any other unchanged values from lower-index iterators.
            while i >= 0:
                result.appendleft(self._contents[i][self._position[i]])
                i -= 1
        return tuple(result)


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


def tee(iterable, n=2):
    return tee_manager(_iter(iterable), n=n).iterators()


class accumulate(BaseItertool):
    def __init__(self, iterable, func=None):
        self._iter = _iter(iterable)
        self._func = func
        self._initialized = False
        self._accumulated = None

    def _combine(self, value):
        if self._func is not None:
            return self._func(self._accumulated, value)
        else:
            return self._accumulated + value

    def __next__(self):
        value = next(self._iter)
        if not self._initialized:
            self._accumulated = value
            self._initialized = True
        else:
            self._accumulated = self._combine(value)
        return self._accumulated


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
