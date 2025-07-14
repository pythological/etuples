from collections.abc import Sequence
from operator import add

from pytest import importorskip, raises

from etuples.core import ExpressionTuple, KwdPair, etuple
from etuples.dispatch import apply, etuplize, rands, rator


class Node:
    __slots__ = ("rator", "rands")

    def __init__(self, rator, rands):
        self.rator, self.rands = rator, rands

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.rator == other.rator
            and self.rands == other.rands
        )


class Operator:
    def __init__(self, op_name):
        self.op_name = op_name

    def __call__(self, *args):
        pass


rands.add((Node,), lambda x: x.rands)
rator.add((Node,), lambda x: x.rator)


@apply.register(Operator, (Sequence, ExpressionTuple))
def apply_Operator(rator, rands):
    return Node(rator, rands)


def test_etuple_apply():
    """Test `etuplize` and `etuple` interactions with `apply`."""

    assert apply(add, (1, 2)) == 3
    assert apply(1, (2,)) == (1, 2)

    # Make sure that we don't lose underlying `evaled_obj`s
    # when taking apart and re-creating expression tuples
    # using `kanren`'s `operator`, `arguments` and `term`
    # functions.
    e1 = etuple(add, (object(),), (object(),))
    e1_obj = e1.evaled_obj

    e1_dup = (rator(e1),) + rands(e1)

    assert isinstance(e1_dup, ExpressionTuple)
    assert e1_dup.evaled_obj == e1_obj

    e1_dup_2 = apply(rator(e1), rands(e1))
    assert e1_dup_2 == e1_obj


def test_rator_rands_apply():
    op = Operator("*")
    node = Node(op, [1, 2])
    node_rtr = rator(node)
    node_rnd = rands(node)

    assert node_rtr == op
    assert node_rnd == [1, 2]
    assert apply(node_rtr, node_rnd) == node


def test_etuplize():
    e0 = etuple(add, 1)
    e1 = etuplize(e0)

    assert e0 is e1

    assert etuple(1, 2) == etuplize((1, 2))

    with raises(TypeError):
        etuplize("ab")

    assert "ab" == etuplize("ab", return_bad_args=True)

    op_1, op_2 = Operator("*"), Operator("+")
    node_1 = Node(op_2, [1, 2])
    node_2 = Node(op_1, [node_1, 3, ()])

    assert etuplize(node_2) == etuple(op_1, etuple(op_2, 1, 2), 3, ())
    assert type(etuplize(node_2)[-1]) == tuple
    assert etuplize(node_2, shallow=True) == etuple(op_1, node_1, 3, ())

    def rands_transform(x):
        if x == 1:
            return 4
        return x

    assert etuplize(node_2, rands_transform_fn=rands_transform) == etuple(
        op_1, etuple(op_2, 4, 2), 3, ()
    )

    def rator_transform(x):
        if x == op_1:
            return op_2
        return x

    assert etuplize(node_2, rator_transform_fn=rator_transform) == etuple(
        op_2, etuple(op_2, 1, 2), 3, ()
    )


def test_unification():
    from cons import cons

    uni = importorskip("unification")

    var, unify, reify = uni.var, uni.unify, uni.reify

    a_lv, b_lv = var(), var()
    assert unify(etuple(add, 1, 2), etuple(add, 1, 2), {}) == {}
    assert unify(etuple(add, 1, 2), etuple(a_lv, 1, 2), {}) == {a_lv: add}
    assert reify(etuple(a_lv, 1, 2), {a_lv: add}) == etuple(add, 1, 2)

    res = unify(etuple(add, 1, 2), cons(a_lv, b_lv), {})
    assert res == {a_lv: add, b_lv: etuple(1, 2)}

    res = reify(cons(a_lv, b_lv), res)
    assert isinstance(res, ExpressionTuple)
    assert res == etuple(add, 1, 2)

    et = etuple(
        a_lv,
    )
    res = reify(et, {a_lv: 1})
    assert isinstance(res, ExpressionTuple)

    et = etuple(
        a_lv,
    )
    # We choose to allow unification with regular tuples.
    if etuple(1) == (1,):
        res = unify(et, (1,))
        assert res == {a_lv: 1}

    et = etuple(add, 1, 2)
    assert et.evaled_obj == 3

    res = unify(et, cons(a_lv, b_lv))
    assert res == {a_lv: add, b_lv: et[1:]}

    # Make sure we've preserved the original object after deconstruction via
    # `unify`
    assert res[b_lv]._parent is et
    assert ((res[a_lv],) + res[b_lv])._evaled_obj == 3

    # Make sure we've preserved the original object after reconstruction via
    # `reify`
    rf_res = reify(cons(a_lv, b_lv), res)
    assert rf_res is et

    et_lv = etuple(add, a_lv, 2)
    assert reify(et_lv[1:], {})._parent is et_lv

    # Reify a logic variable to another logic variable
    assert reify(et_lv[1:], {a_lv: b_lv})._parent is et_lv

    # TODO: We could propagate the parent etuple when a sub-etuple is `cons`ed
    # with logic variables.
    # et_1 = et[2:]
    # et_2 = cons(b_lv, et_1)
    # assert et_2._parent is et
    # assert reify(et_2, {a_lv: 1})._parent is et

    e1 = KwdPair("name", "blah")
    e2 = KwdPair("name", a_lv)
    assert unify(e1, e2, {}) == {a_lv: "blah"}
    assert reify(e2, {a_lv: "blah"}) == e1

    e1 = etuple(add, 1, name="blah")
    e2 = etuple(add, 1, name=a_lv)
    assert unify(e1, e2, {}) == {a_lv: "blah"}
    assert reify(e2, {a_lv: "blah"}) == e1
