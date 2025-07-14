import sys
from operator import add
from types import GeneratorType

import pytest

from etuples.core import ExpressionTuple, InvalidExpression, KwdPair, etuple


def test_ExpressionTuple(capsys):
    e0 = ExpressionTuple((add, 1, 2))
    assert hash(e0) == hash((add, 1, 2))
    assert e0 == ExpressionTuple(e0)

    e5 = ExpressionTuple((1, ExpressionTuple((2, 3))))
    e6 = ExpressionTuple((1, ExpressionTuple((2, 3))))

    assert e5 == e6
    assert hash(e5) == hash(e6)
    assert ExpressionTuple((ExpressionTuple((1,)), 2)) != ExpressionTuple((1, 2))

    # Not sure if we really want this; it's more
    # common to have a copy constructor, no?
    assert e0 is ExpressionTuple(e0)

    e0_2 = e0[:2]
    assert e0_2 == (add, 1)
    assert e0_2._parent is e0
    assert e0_2 + (2,) is e0
    assert (add, 1) + e0[-1:] is e0
    assert 1 in e0
    assert e0[1:] > (1,) and e0[1:] >= (1,)
    assert e0[1:] < (3, 3) and e0[1:] <= (3, 3)
    assert isinstance(e0 * 2, ExpressionTuple)
    assert e0 * 2 == ExpressionTuple((add, 1, 2, add, 1, 2))
    assert isinstance(2 * e0, ExpressionTuple)
    assert 2 * e0 == ExpressionTuple((add, 1, 2, add, 1, 2))

    e1 = ExpressionTuple((add, e0, 3))
    assert e1.evaled_obj == 6

    # ("_evaled_obj", "_tuple", "_parent")
    e2 = e1[1:2]
    assert e2._parent is e1

    assert e2 == ExpressionTuple((e0,))

    ExpressionTuple((print, "hi")).evaled_obj
    captured = capsys.readouterr()
    assert captured.out == "hi\n"

    e3 = ExpressionTuple(())

    with pytest.raises(InvalidExpression):
        e3.evaled_obj

    e4 = ExpressionTuple((1,))

    with pytest.raises(InvalidExpression):
        e4.evaled_obj

    assert ExpressionTuple((ExpressionTuple((lambda: add,)), 1, 1)).evaled_obj == 2
    assert ExpressionTuple((1, 2)) != ExpressionTuple((1,))
    assert ExpressionTuple((1, 2)) != ExpressionTuple((1, 3))

    with pytest.warns(DeprecationWarning):
        ExpressionTuple((print, "hi")).eval_obj


def test_eval_apply_fn():
    class Add(object):
        def __call__(self):
            return None

        def add(self, x, y):
            return x + y

    class AddExpressionTuple(ExpressionTuple):
        def _eval_apply_fn(self, op):
            return op.add

    op = Add()
    assert AddExpressionTuple((op, 1, 2)).evaled_obj == 3


def test_etuple():
    """Test basic `etuple` functionality."""

    def test_op(*args):
        return tuple(object() for i in range(sum(args)))

    e1 = etuple(test_op, 1, 2)

    assert e1._evaled_obj is ExpressionTuple.null

    with pytest.raises(ValueError):
        e1.evaled_obj = 1

    e1_obj = e1.evaled_obj
    assert len(e1_obj) == 3
    assert all(type(o) is object for o in e1_obj)

    # Make sure we don't re-create the cached `evaled_obj`
    e1_obj_2 = e1.evaled_obj
    assert e1_obj == e1_obj_2

    # Confirm that evaluation is recursive
    e2 = etuple(add, (object(),), e1)

    # Make sure we didn't convert this single tuple value to
    # an `etuple`
    assert type(e2[1]) is tuple

    # Slices should be `etuple`s, though.
    assert isinstance(e2[:1], ExpressionTuple)
    assert e2[1] == e2[1:2][0]

    e2_obj = e2.evaled_obj

    assert type(e2_obj) is tuple
    assert len(e2_obj) == 4
    assert all(type(o) is object for o in e2_obj)
    # Make sure that it used `e1`'s original `evaled_obj`
    assert e2_obj[1:] == e1_obj

    # Confirm that any combination of `tuple`s/`etuple`s in
    # concatenation result in an `etuple`
    e_radd = (1,) + etuple(2, 3)
    assert isinstance(e_radd, ExpressionTuple)
    assert e_radd == (1, 2, 3)

    e_ladd = etuple(1, 2) + (3,)
    assert isinstance(e_ladd, ExpressionTuple)
    assert e_ladd == (1, 2, 3)


def test_etuple_generator():
    e_gen = etuple(lambda v: (i for i in v), range(3))
    e_gen_res = e_gen.evaled_obj
    assert isinstance(e_gen_res, GeneratorType)
    assert tuple(e_gen_res) == tuple(range(3))


def test_etuple_kwargs():
    """Test keyword arguments and default argument values."""

    e = etuple(a=1, b=2)
    assert e._tuple == (KwdPair("a", 1), KwdPair("b", 2))
    assert KwdPair("a", 1) in e._tuple
    assert hash(KwdPair("a", 1)) == hash(KwdPair("a", 1))

    def test_func(a, b, c=None, d="d-arg", **kwargs):
        assert isinstance(c, (type(None), int))
        return [a, b, c, d]

    e1 = etuple(test_func, 1, 2)
    assert e1.evaled_obj == [1, 2, None, "d-arg"]

    # Make sure we handle variadic args properly
    def test_func2(*args, c=None, d="d-arg", **kwargs):
        assert isinstance(c, (type(None), int))
        return list(args) + [c, d]

    e0 = etuple(test_func2, c=3)
    assert e0.evaled_obj == [3, "d-arg"]

    e11 = etuple(test_func2, 1, 2)
    assert e11.evaled_obj == [1, 2, None, "d-arg"]

    e2 = etuple(test_func, 1, 2, 3)
    assert e2.evaled_obj == [1, 2, 3, "d-arg"]

    e3 = etuple(test_func, 1, 2, 3, 4)
    assert e3.evaled_obj == [1, 2, 3, 4]

    e4 = etuple(test_func, 1, 2, c=3)
    assert e4.evaled_obj == [1, 2, 3, "d-arg"]

    e5 = etuple(test_func, 1, 2, d=3)
    assert e5.evaled_obj == [1, 2, None, 3]

    e6 = etuple(test_func, 1, 2, 3, d=4)
    assert e6.evaled_obj == [1, 2, 3, 4]

    # Try evaluating nested etuples
    e7 = etuple(test_func, etuple(add, 1, 0), 2, c=etuple(add, 1, etuple(add, 1, 1)))
    assert e7.evaled_obj == [1, 2, 3, "d-arg"]

    # Try a function without an obtainable signature object
    e8 = etuple(
        enumerate,
        etuple(list, ["a", "b", "c", "d"]),
        start=etuple(add, 1, etuple(add, 1, 1)),
    )
    assert list(e8.evaled_obj) == [(3, "a"), (4, "b"), (5, "c"), (6, "d")]

    # Use "evaled_obj" kwarg and make sure it doesn't end up in the `_tuple` object
    e9 = etuple(add, 1, 2, evaled_obj=3)
    assert e9._tuple == (add, 1, 2)
    assert e9._evaled_obj == 3


def test_str():
    et = etuple(1, etuple("a", 2), etuple(3, "b"))
    assert (
        repr(et)
        == "ExpressionTuple((1, ExpressionTuple(('a', 2)), ExpressionTuple((3, 'b'))))"
    )
    assert str(et) == "e(1, e(a, 2), e(3, b))"

    kw = KwdPair("a", 1)

    assert repr(kw) == "KwdPair('a', 1)"
    assert str(kw) == "a=1"


def test_pprint():
    pretty_mod = pytest.importorskip("IPython.lib.pretty")
    et = etuple(1, etuple("a", *range(20)), etuple(3, "b"), blah=etuple("c", 0))
    assert (
        pretty_mod.pretty(et)
        == "e(\n  1,\n  e('a', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19),\n  e(3, 'b'),\n  blah=e(c, 0))"  # noqa: E501
    )


def gen_long_add_chain(N=None, num=1):
    b_struct = num
    if N is None:
        N = sys.getrecursionlimit()
    for i in range(0, N):
        b_struct = etuple(add, num, b_struct)
    return b_struct


def test_reify_recursion_limit():
    a = gen_long_add_chain(10)
    assert a.evaled_obj == 11

    r_limit = sys.getrecursionlimit()

    try:
        sys.setrecursionlimit(100)

        a = gen_long_add_chain(200)
        assert a.evaled_obj == 201

        b = gen_long_add_chain(200, num=2)
        assert b.evaled_obj == 402

        c = gen_long_add_chain(200)
        assert a == c

    finally:
        sys.setrecursionlimit(r_limit)


@pytest.mark.skip(
    reason=(
        "This will cause an unrecoverable stack overflow"
        " in some cases (e.g. GitHub Actions' default ubuntu-latest runners)"
    )
)
@pytest.mark.xfail(strict=True)
def test_reify_recursion_limit_hash():
    r_limit = sys.getrecursionlimit()

    try:
        sys.setrecursionlimit(100)
        a = gen_long_add_chain(200)
        # CPython uses the call stack and fails
        assert hash(a)
    finally:
        sys.setrecursionlimit(r_limit)
