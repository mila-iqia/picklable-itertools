from unittest import SkipTest
from picklable_itertools.extras import partition, partition_all

from . import verify_same, verify_pickle


def test_partition():
    try:
        from toolz import itertoolz
    except ImportError:
        raise SkipTest()
    for obj, ref in zip([partition, partition_all],
                        [itertoolz.partition, itertoolz.partition_all]):
        yield verify_same, obj, ref, None, 2, [5, 9, 2, 6]
        yield verify_same, obj, ref, None, 2, [5, 9, 2], 3
        yield verify_same, obj, ref, None, 3, [5], 'a'
        yield verify_same, obj, ref, None, 3, [5, 9, 2, 9, 2]
        yield verify_same, obj, ref, None, 3, [5, 9, 2, 9, 2]
        yield verify_pickle, obj, ref, 2, 1, 3, [5, 9, 2, 9, 2, 4, 3]
