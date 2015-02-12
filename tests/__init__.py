import functools
import itertools
import random
import tempfile

import six
from six.moves import cPickle
from six.moves import xrange
from nose.tools import assert_raises
from unittest import SkipTest

from picklable_itertools import (
    repeat, chain, compress, count, cycle, ifilter, ifilterfalse, imap, izip,
    file_iterator, ordered_sequence_iterator, zip_longest, _iter, islice,
    range_iterator, product, tee, accumulate, takewhile, dropwhile
)
_map = map if six.PY3 else itertools.imap
_zip = zip if six.PY3 else itertools.izip
_zip_longest = itertools.zip_longest if six.PY3 else itertools.izip_longest
_filter = filter if six.PY3 else itertools.ifilter
_filterfalse = itertools.filterfalse if six.PY3 else itertools.ifilterfalse
_islice = itertools.islice


def verify_same(picklable_version, reference_version, n, *args, **kwargs):
    """Take a reference version from itertools, verify the same operation
    in our version.
    """
    try:
        expected = reference_version(*args, **kwargs)
    except Exception as e:
        assert_raises(e.__class__, picklable_version, *args, **kwargs)
        return
    actual = picklable_version(*args, **kwargs)
    done = 0
    while done != n:
        try:
            expected_val = next(expected)
        except StopIteration:
            check_stops(actual)
            break
        try:
            actual_val = next(actual)
        except StopIteration:
            assert False, "prematurely exhausted; expected {}".format(
                str(expected_val))
        assert expected_val == actual_val
        done += 1


def verify_pickle(picklable_version, reference_version, n, m, *args, **kwargs):
    """Take n steps, pickle at m < n, and make sure it continues the same."""
    expected = reference_version(*args, **kwargs)
    actual = picklable_version(*args, **kwargs)
    done = 0
    if not m < n:
        raise ValueError("Test only makes sense with m < n")
    while done != n:
        expected_val = next(expected)
        actual_val = next(actual)
        assert expected_val == actual_val
        if done == m:
            actual = cPickle.loads(cPickle.dumps(actual))
        done += 1


def check_stops(it):
    """Verify that an exhausted iterator yields StopIteration."""
    try:
        val = next(it)
    except StopIteration:
        return
    assert False, "expected exhausted iterator; got {}".format(str(val))


def test_ordered_sequence_iterator():
    yield verify_same, ordered_sequence_iterator, iter, None, []
    yield verify_same, ordered_sequence_iterator, iter, None, ()
    yield verify_same, ordered_sequence_iterator, iter, None, [5, 2]
    yield verify_same, ordered_sequence_iterator, iter, None, ("D", "X", "J")


def test_dict_iterator():
    d = {'a': 'b', 1: 2}
    assert list(_iter(d)) == list(iter(d))
    assert list(_iter(d.items())) == list(iter(d.items()))
    assert list(_iter(d.keys())) == list(iter(d.keys()))
    assert list(_iter(d.values())) == list(iter(d.values()))

    yield verify_pickle, _iter, iter, 2, 1, d
    yield verify_pickle, _iter, iter, 2, 1, d.items()
    yield verify_pickle, _iter, iter, 2, 1, d.values()
    yield verify_pickle, _iter, iter, 2, 1, d.keys()


def test_range_iterator():
    yield verify_same, range_iterator, iter, None, xrange(5)
    yield verify_same, range_iterator, iter, None, xrange(2, 5)
    yield verify_same, range_iterator, iter, None, xrange(5, 2)
    yield verify_same, range_iterator, iter, None, xrange(0)
    yield verify_same, range_iterator, iter, None, xrange(-3)
    yield verify_same, range_iterator, iter, None, xrange(-5, -3)
    yield verify_same, range_iterator, iter, None, xrange(-5, -1, -2)
    yield verify_same, range_iterator, iter, None, xrange(-5, -1, 2)
    yield verify_same, range_iterator, iter, None, xrange(2, 5, 7)
    yield verify_same, range_iterator, iter, None, xrange(2, 7, -1)
    yield verify_same, range_iterator, iter, None, xrange(5, 3, -1)
    yield verify_same, range_iterator, iter, None, xrange(5, 4, -2)


def _create_test_file():
    f = tempfile.NamedTemporaryFile(mode='w')
    f.write("\n".join(map(str, range(4))))
    f.flush()
    return f


def test_file_iterator():
    f = _create_test_file()
    assert list(file_iterator(open(f.name))) == list(iter(open(f.name)))


def test_file_iterator_pickling():
    f = _create_test_file()
    it = _iter(open(f.name))
    last = [next(it) for _ in range(2)][-1]
    first = next(cPickle.loads(cPickle.dumps(it)))
    assert int(first) == int(last) + 1


def test_repeat():
    yield verify_same, repeat, itertools.repeat, None, 5, 0
    yield verify_same, repeat, itertools.repeat, None, 'abc', 5
    yield verify_same, repeat, itertools.repeat, None, 'def', 3


def test_chain():
    yield verify_same, chain, itertools.chain, None, [5, 4], [3], [9, 10]
    yield verify_same, chain, itertools.chain, None, [3, 1], [], ['x', 'y']
    yield verify_same, chain, itertools.chain, None, [], [], []
    yield verify_same, chain, itertools.chain, None


def test_compress():
    yield verify_same, compress, itertools.compress, None, [1, 2, 3], [1, 2, 3]
    yield verify_same, compress, itertools.compress, None, [1, 2, 3], [1, 0, 0]
    yield verify_same, compress, itertools.compress, None, [1, 2, 3], [1, 0]
    yield verify_same, compress, itertools.compress, None, [1, 2], [1, 0, 1]
    yield verify_same, compress, itertools.compress, None, [1, 2], [0, 0]
    yield verify_same, compress, itertools.compress, None, [1, 2], [0]
    yield verify_same, compress, itertools.compress, None, [1, 2], [0, 0, 0]


def test_count():
    yield verify_same, count, itertools.count, 6
    yield verify_same, count, itertools.count, 20, 2
    yield verify_same, count, itertools.count, 10, 5, 9
    yield verify_same, count, itertools.count, 30, 3, 10


def test_cycle():
    yield verify_same, cycle, itertools.cycle, 40, [4, 9, 10]
    yield verify_same, cycle, itertools.cycle, 10, [4, 9, 20, 10]
    yield verify_same, cycle, itertools.cycle, 20, [4, 9, 30, 10, 9]
    yield verify_same, cycle, itertools.cycle, 60, [8, 4, 5, 4, 9, 10]
    yield verify_same, cycle, itertools.cycle, None, []


def test_imap():
    yield verify_same, imap, _map, None, lambda x: x + 2, [3, 4, 5]
    yield verify_same, imap, _map, None, lambda x, y: x + y, [3, 4], [9, 2]
    yield verify_same, imap, _map, None, lambda x, y: x + y, [3], [9, 2]
    yield verify_same, imap, _map, None, lambda x, y: x + y, [3], [9, 2], []


def test_izip():
    yield verify_same, izip, _zip, None, [3, 4, 5]
    yield verify_same, izip, _zip, None, [3, 4], [9, 2]
    yield verify_same, izip, _zip, None, [3], [9, 2]
    yield verify_same, izip, _zip, None, [3], [9, 2], []


def test_ifilter():
    yield verify_same, ifilter, _filter, None, lambda x: x >= 4, [3, 4, 5]
    yield verify_same, ifilter, _filter, None, lambda x: x >= 6, [3, 4, 5]
    yield verify_same, ifilter, _filter, None, lambda x: x < 3, []
    yield verify_same, ifilter, _filter, None, None, [0, 3, 0, 0, 1]


def test_ifilterfalse():
    yield (verify_same, ifilterfalse, _filterfalse, None,
           lambda x: x >= 4, [3, 4, 5])
    yield (verify_same, ifilterfalse, _filterfalse, None,
           lambda x: x >= 6, [3, 4, 5])
    yield (verify_same, ifilterfalse, _filterfalse, None,
           lambda x: x < 3, [])
    yield (verify_same, ifilterfalse, _filterfalse, None,
           None, [0, 3, 0, 0, 1])


def test_product():
    yield verify_same, product, itertools.product, None
    yield verify_same, product, itertools.product, None, []
    yield verify_same, product, itertools.product, None, [], []
    yield verify_same, product, itertools.product, None, [], [], []
    yield verify_same, product, itertools.product, None, [5]
    yield verify_same, product, itertools.product, None, [5], []
    yield verify_same, product, itertools.product, None, [], [5], []
    yield verify_same, product, itertools.product, None, [2, 5], [3, 5, 9]
    yield verify_same, product, itertools.product, None, [2, 5], [1], [3, 5, 9]
    yield (verify_same, functools.partial(product, repeat=3),
           functools.partial(itertools.product, repeat=3), None, [1, 2, 3])
    yield (verify_same, functools.partial(product, repeat=4),
           functools.partial(itertools.product, repeat=4), None, [1], [1, 2])
    yield (verify_same, functools.partial(product, repeat=2),
           functools.partial(itertools.product, repeat=2), None, [3, 1], [1])
    yield (verify_same, functools.partial(product, repeat=3),
           functools.partial(itertools.product, repeat=3), None, [])
    yield (verify_same, functools.partial(product, repeat=3),
           functools.partial(itertools.product, repeat=3), None, [], [3])
    yield (verify_same, functools.partial(product, repeat=3),
           functools.partial(itertools.product, repeat=3), None, [1], [])
    yield (verify_pickle, product, itertools.product, 8, 3, [1, 2], [2, 3],
           [5, 6])
    yield (verify_pickle, functools.partial(product, repeat=3),
           functools.partial(itertools.product, repeat=3), 50, 45,
           [1, 2], [3, 4])


def test_zip_longest():
    yield (verify_same, zip_longest, _zip_longest, None, [], [])
    yield (verify_same, zip_longest, _zip_longest, None, [], [5, 4])
    yield (verify_same, zip_longest, _zip_longest, None, [2], [5, 4])
    yield (verify_same, zip_longest, _zip_longest, None, [7, 9], [5, 4])
    yield (verify_same, zip_longest, _zip_longest, None, [7, 9],
           [4], [2, 9, 3])
    yield (verify_same, zip_longest, _zip_longest, None, [7, 9], [4], [])
    yield (verify_same, zip_longest, _zip_longest, None, [7], [4], [],
           [5, 9])
    yield (verify_same, functools.partial(zip_longest, fillvalue=-1),
           functools.partial(_zip_longest, fillvalue=-1),
           [7], [4], [], [5, 9])

    yield (verify_pickle, zip_longest, _zip_longest, 3, 2, [7, 9, 8], [1, 2])
    yield (verify_pickle, zip_longest, _zip_longest, 3, 1, [7, 9, 8], [1, 2])


def test_islice():
    yield (verify_same, islice, _islice, None, [], 0)
    yield (verify_same, islice, _islice, None, [1], 0)
    yield (verify_same, islice, _islice, None, [1], 1)
    yield (verify_same, islice, _islice, None, [1], 3)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 5)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 1, 2)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 1, 5, 3)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 0, 3, 2)
    yield (verify_same, islice, _islice, None, [1, 2, 3, 4, 5], 1, 4, 3)
    yield (verify_same, islice, _islice, None, [1, 2, 3, 4, 5], -2, 9, 4)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 4, 9)
    yield (verify_same, islice, _islice, None, [1, 2, 3], 0, 9, 5)

    yield (verify_pickle, islice, _islice, 3, 2, [1, 2, 3], 5)


def verify_tee(n, original, seed):
    try:
        state = random.getstate()
        iterators = tee(original, n=n)
        results = [[] for i in range(n)]
        exhausted = [False] * n
        while not all(exhausted):
            i = random.randint(0, n - 1)
            if not exhausted[i]:
                if len(results[i]) == len(original):
                    assert_raises(StopIteration, next, iterators[i])
                    assert results[i] == original
                    exhausted[i] = True
                else:
                    elem = next(iterators[i])
                    results[i].append(elem)
    finally:
        random.setstate(state)


def test_tee():
    yield verify_tee, 2, [5, 2, 4], 1
    yield verify_tee, 3, [5, 2, 4, 6, 9], 2
    yield verify_tee, 5, [5, 2, 4, 6, 9], 3
    yield verify_tee, 6, [], 3


def test_accumulate():
    if not six.PY3:
        raise SkipTest()
    yield verify_same, accumulate, itertools.accumulate, [5, 4, 9]
    yield verify_same, accumulate, itertools.accumulate, ['a', 'b', 'c']
    yield verify_same, accumulate, itertools.accumulate, [[1], [2], [3, 4]]
    yield (verify_same, accumulate, itertools.accumulate, [9, 1, 2],
           lambda x, y: x - y)


def test_takewhile():
    base = (verify_same, takewhile, itertools.takewhile, None)
    yield base + (bool,)
    yield base + (bool, [])
    yield base + (bool, [0, 0, 5])
    yield base + (bool, [1, 2, 0, 4, 0])
    yield base + (lambda x: x > 3, range(5, 0, -1))

def test_dropwhile():
    base = (verify_same, dropwhile, itertools.dropwhile, None)
    yield base + (bool,)
    yield base + (bool, [])
    yield base + (bool, [5, 5, 2, 0, 0])
    yield base + (bool, [1, 2, 0, 4, 0])
    yield base + (lambda x: x > 3, range(5, 0, -1))
