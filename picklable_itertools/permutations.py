from abc import ABCMeta, abstractmethod
import six
from .product import product
from .base import BaseItertool


@six.add_metaclass(ABCMeta)
class IndexBased(BaseItertool):
    def __init__(self, iterable, r=None):
        self._pool = tuple(iterable)
        self._r = r if r is not None else len(self._pool)
        self._iter = self._construct_iter()

    def _construct_iter(self):
        return product(range(len(self._pool)), repeat=self._r)

    @abstractmethod
    def _valid_indices(self, indices):
        pass

    def __next__(self):
        indices = next(self._iter)
        while not self._valid_indices(indices):
            indices = next(self._iter)
        return tuple(self._pool[i] for i in indices)


class permutations(IndexBased):
    def _valid_indices(self, indices):
        return len(set(indices)) == self._r


@six.add_metaclass(ABCMeta)
class AbstractCombinations(IndexBased):
    def __init__(self, iterable, r):
        super(AbstractCombinations, self).__init__(iterable, r)

    def _valid_indices(self, indices):
        return sorted(indices) == list(indices)


class combinations_with_replacement(AbstractCombinations):
    pass


class combinations(AbstractCombinations):
    def _construct_iter(self):
        return permutations(range(len(self._pool)), self._r)
