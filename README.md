# picklable_itertools

A reimplementation of the Python standard library's `itertools`, in Python,
using picklable iterator objects. Intended to be Python 2.7 and 3.4+
compatible.

## Why?
* Because the standard library pickle module (nor the excellent
  [dill](https://github.com/uqfoundation/dill) package) can't serialize
  generators, of which all the objects in `itertools` are instances.
* Because there are lots of instances where these things in `itertools` would
  simplify code, but can't be used because serializability must be maintained.
  Primarily [blocks](https://github.com/bartvm/blocks) is our first consumer.

## Philosophy
* _This should be a drop-in replacement._ Pretty self-explanatory. Test
  against the standard library `itertools` or builtin implementation to
  verify behaviour matches.
* _Handle built-in types gracefully if possible._ List iterators, etc.
  are not picklable on Python 2.x, so we provide an alternative implementation.
  set and dict iterators demand a bit more thought.
* _Premature optimization is the root of all evil._ These things are
  implemented in Python, so speed is obviously not our primary concern. Several
  of the more advanced iterators are constructed by chaining simpler iterators
  together, which is not the most efficient thing to do but simplifies the
  code a lot. If it turns out that speed (or a shallower object graph) is
  necessary or desirable, these can always be reimplemented. Pull requests
  to this effect are welcome.
