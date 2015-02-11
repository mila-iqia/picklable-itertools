import itertools
import six

from picklable_itertools import (
    repeat, chain, compress, count, cycle, imap, izip,
    ordered_sequence_iterator
)
_map = map if six.PY3 else itertools.imap
_zip = zip if six.PY3 else itertools.izip


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
