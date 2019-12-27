from collections.abc import Callable, Sequence, Mapping

from multipledispatch import dispatch

from cons.core import ConsError, ConsNull, ConsPair, car, cdr, cons

from .core import etuple, ExpressionTuple

try:
    from unification.core import _reify, _unify
except ModuleNotFoundError:
    pass
else:

    def _unify_ExpressionTuple(u, v, s):
        return _unify(u._tuple, v._tuple, s)

    _unify.add((ExpressionTuple, ExpressionTuple, Mapping), _unify_ExpressionTuple)

    def _reify_ExpressionTuple(u, s):
        return etuple(*_reify(u._tuple, s))

    _reify.add((ExpressionTuple, Mapping), _reify_ExpressionTuple)


@dispatch(object)
def rator(x):
    return car(x)


@dispatch(object)
def rands(x):
    return cdr(x)


@dispatch(object, Sequence)
def apply(rator, rands):
    res = cons(rator, rands)
    return etuple(*res)


@apply.register(Callable, Sequence)
def apply_Sequence(rator, rands):
    return rator(*rands)


@apply.register(Callable, ExpressionTuple)
def apply_ExpressionTuple(rator, rands):
    return ((rator,) + rands).eval_obj


# These are used to maintain some parity with the old `kanren.term` API
operator, arguments, term = rator, rands, apply


@dispatch(object)
def etuplize(x, shallow=False, return_bad_args=False):
    """Return an expression-tuple for an object (i.e. a tuple of rand and rators).

    When evaluated, the rand and rators should [re-]construct the object.  When
    the object cannot be given such a form, it is simply converted to an
    `ExpressionTuple` and returned.

    Parameters
    ----------
    x: object
      Object to convert to expression-tuple form.
    shallow: bool
      Whether or not to do a shallow conversion.
    return_bad_args: bool
      Return the passed argument when its type is not appropriate, instead
      of raising an exception.

    """
    if isinstance(x, ExpressionTuple):
        return x
    elif x is not None and isinstance(x, (ConsNull, ConsPair)):
        return etuple(*x)

    try:
        op, args = rator(x), rands(x)
    except ConsError:
        op, args = None, None

    if not callable(op) or not isinstance(args, (ConsNull, ConsPair)):
        if return_bad_args:
            return x
        else:
            raise TypeError(f"x is neither a non-str Sequence nor term: {type(x)}")

    if shallow:
        et_op = op
        et_args = args
    else:
        et_op = etuplize(op, return_bad_args=True)
        et_args = tuple(etuplize(a, return_bad_args=True) for a in args)

    res = etuple(et_op, *et_args, eval_obj=x)
    return res
