import os.path

from pkg_resources import get_distribution, DistributionNotFound

from .filter import ifilter, ifilterfalse, takewhile, dropwhile
from .grouping import groupby
from .iter_dispatch import (
    _iter, ordered_sequence_iterator, file_iterator, range_iterator
)
from .map_zip import imap, starmap, izip, izip_longest
from .permutations import (
    permutations, combinations, combinations_with_replacement
)
from .product import product
from .range import xrange
from .simple import accumulate, chain, compress, count, cycle, repeat
from .slicing import islice
from .tee import tee

# Python 3 equivalents.
filter = ifilter
filterfalse = ifilterfalse
zip = izip
zip_longest = izip_longest


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


__all__ = ['ifilter', 'ifilterfalse', 'takewhile', 'dropwhile', 'groupby',
           '_iter', 'ordered_sequence_iterator', 'file_iterator',
           'range_iterator', 'imap', 'starmap', 'izip', 'izip_longest',
           'permutations', 'combinations', 'combinations_with_replacement',
           'accumulate', 'chain', 'compress', 'count', 'cycle', 'repeat',
           'islice', 'tee', 'filter', 'filterfalse', 'zip', 'zip_longest']
