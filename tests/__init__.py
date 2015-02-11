import itertools
from picklable_itertools import repeat, chain, ordered_sequence_iterator


def verify_same(picklable_version, reference_version, *args, **kwargs):
    """Take a reference version from itertools, verify the same operation
    in our version.
    """
    expected = reference_version(*args, **kwargs)
    actual = picklable_version(*args, **kwargs)
    while True:
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


def check_stops(it):
    """Verify that an exhausted iterator yields StopIteration."""
    try:
        val = next(it)
    except StopIteration:
        return
    assert False, "expected exhausted iterator; got {}".format(str(val))


def test_ordered_sequence_iterator():
    yield verify_same, ordered_sequence_iterator, iter, []
    yield verify_same, ordered_sequence_iterator, iter, ()
    yield verify_same, ordered_sequence_iterator, iter, [5, 2]
    yield verify_same, ordered_sequence_iterator, iter, ("Matt", "Mark", "Luke")


def test_repeat():
    yield verify_same, repeat, itertools.repeat, 5, 0
    yield verify_same, repeat, itertools.repeat, 'abc', 5
    yield verify_same, repeat, itertools.repeat, 'def', 3


def test_chain():
    yield verify_same, chain, itertools.chain, [5, 4], [3], [9, 10]
    yield verify_same, chain, itertools.chain, [3, 1], [], ['x', 'y']
    yield verify_same, chain, itertools.chain, [], [], []
    yield verify_same, chain, itertools.chain
