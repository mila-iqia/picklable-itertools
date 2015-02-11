import functools
import itertools
import six
import tempfile
from six.moves import cPickle

from picklable_itertools import (
    repeat, chain, compress, count, cycle, ifilter, ifilterfalse, imap, izip,
    file_iterator, ordered_sequence_iterator, zip_longest, _iter
)
_map = map if six.PY3 else itertools.imap
_zip = zip if six.PY3 else itertools.izip
_zip_longest = itertools.zip_longest if six.PY3 else itertools.izip_longest
_filter = filter if six.PY3 else itertools.ifilter
_filterfalse = itertools.filterfalse if six.PY3 else itertools.ifilterfalse


def verify_same(picklable_version, reference_version, n, *args, **kwargs):
    """Take a reference version from itertools, verify the same operation
    in our version.
    """
    expected = reference_version(*args, **kwargs)
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
