from numbers import Integral
from .iter_dispatch import range_iterator


__all__ = ['xrange']


def _check_integral(value):
    if not isinstance(value, Integral):
        raise TypeError("'{}' object cannot be interpreted "
                        "as an integer".format(type(value).__name__))


class xrange(object):
    """A replacement for Python 3 `range()` (and Python 2 `xrange()`) that
    yields picklable iterators when iterated upon.
    """
    __slots__ = ['_start', '_stop', '_step']

    def __init__(self, *args):
        self._start = 0
        self._step = 1
        if len(args) == 0:
            raise TypeError("{} expected 1 arguments, got 0".format(
                self.__class__.__name__))
        elif len(args) == 1:
            self._stop = args[0]
            self._start = 0
        elif len(args) >= 2:
            self._start = args[0]
            self._stop = args[1]
        if len(args) == 3:
            self._step = args[2]
        if len(args) > 3:
            raise TypeError("{} expected at most 3 arguments, got {}".format(
                self.__class__.__name__, len(args)))
        _check_integral(self._start)
        _check_integral(self._stop)
        _check_integral(self._step)

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    def __reduce__(self):
        return (self.__class__, (self.start, self.stop, self.step))

    def __iter__(self):
        return range_iterator(self)
