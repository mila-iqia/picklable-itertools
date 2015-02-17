import collections

from .base import BaseItertool
from .iter_dispatch import _iter
from .tee import tee
_zip = zip


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
