from abc import ABCMeta, abstractmethod
import collections
import io
import six
import sys

from picklable_itertools.version import __version__  # noqa


@six.add_metaclass(ABCMeta)
class BaseItertool(six.Iterator):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        pass


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
                not 0 <= stop <= sys.maxsize):
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
