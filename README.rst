picklable-itertools
===================

A reimplementation of the Python standard library's `itertools`, in Python,
using picklable iterator objects. Intended to be Python 2.7 and 3.4+
compatible.

Why?
----
* Because the standard library pickle module (nor the excellent dill_ package)
  can't serialize all of the `itertools` iterators.
* Because there are lots of instances where these things in `itertools` would
  simplify code, but can't be used because serializability must be maintained.
  Primarily blocks_ is our first consumer. We'd like to be able to serialize
  the entire state of a long-running program for later resumption. We can't
  do this with non-picklable objects.

.. _dill: https://github.com/uqfoundation/dill
.. _blocks: https://github.com/bartvm/blocks

Philosophy
----------
* *This should be a drop-in replacement.* Pretty self-explanatory. Test
  against the standard library ``itertools`` or builtin implementation to
  verify behaviour matches. Where Python 2 and Python 3 differ in their
  naming, (`filterfalse` vs `ifilterfalse`, `zip_longest` vs. `izip_longest`)
  we provide both. We also provide names that were only available in the
  Python 2 incarnation of `itertools` (`ifilter`, `izip`), also available
  under their built-in names in Python 3 (`filter`, `zip`), for convenience.
* *Handle built-in types gracefully if possible.* List iterators, etc.
  are not picklable on Python 2.x, so we provide an alternative
  implementation. File iterators are handled transparently as well. set
  and dict iterators demand a bit more thought.
* *Premature optimization is the root of all evil.* These things are
  implemented in Python, so speed is obviously not our primary concern. Several
  of the more advanced iterators are constructed by chaining simpler iterators
  together, which is not the most efficient thing to do but simplifies the
  code a lot. If it turns out that speed (or a shallower object graph) is
  necessary or desirable, these can always be reimplemented. Pull requests
  to this effect are welcome.
