"""Related things that aren't part of the standard library's `itertools`.

Currently home to picklable reimplementations of a few of the generators
from Matthew Rocklin's Toolz package.

Docstrings for `partition` and `partition_all` are lifted wholesale
from the Toolz documentation <http://toolz.readthedocs.org/en/latest/>.
"""
import six
from .base import BaseItertool
from .map_zip import izip_longest
from .iter_dispatch import iter_


class partition(BaseItertool):
    """Partition sequence into tuples of length n

    >>> list(partition(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    If length of `seq` is not evenly divisible by `n`, the final
    tuple is dropped if `pad` is not specified, or filled to length
    `n` by `pad`:

    >>> list(partition(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4)]

    >>> list(partition(2, [1, 2, 3, 4, 5], pad=None))
    [(1, 2), (3, 4), (5, None)]

    See Also:
        partition_all
    """
    _NO_PAD = '__no_pad__'

    def __init__(self, n, seq, pad=_NO_PAD):
        self._n = n
        self._partition_all = partition_all(n, seq)
        self._pad = pad

    def __next__(self):
        items = next(self._partition_all)
        if len(items) < self._n:
            if self._pad != self._NO_PAD:
                items += (self._pad,) * (self._n - len(items))
            else:
                raise StopIteration
        return items


class partition_all(BaseItertool):
    """Partition all elements of sequence into tuples of length at most n

    The final tuple may be shorter to accommodate extra elements.

    >>> list(partition_all(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]
    >>> list(partition_all(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4), (5,)]

    See Also:
        partition
    """
    def __init__(self, n, seq):
        self._n = n
        self._seq = iter_(seq)

    def __next__(self):
        items = []
        try:
            for _ in six.moves.xrange(self._n):
                items.append(next(self._seq))
        except StopIteration:
            pass
        if len(items) == 0:
            raise StopIteration
        return tuple(items)


class NoMoreItems(object):
    """Sentinel value for `equizip`. Do not use for any other purpose."""
    pass


class IterableLengthMismatch(ValueError):
    """Raised if an iterator passed to `equizip` is shorter than others."""
    pass


class equizip(izip_longest):
    """Like `izip_longest` but ensures the sequences are the same length.

    Raises :class:`IterableLengthMismatch` if one of the iterators
    terminates prematurely.
    """
    def __init__(self, *args):
        super(equizip, self).__init__(*args, fillvalue=NoMoreItems)

    def __next__(self):
        next_item = super(equizip, self).__next__()
        if any(value is NoMoreItems for value in next_item):
            raise IterableLengthMismatch
        return next_item
