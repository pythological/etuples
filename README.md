# `etuples`

[![Build Status](https://travis-ci.org/pythological/etuples.svg?branch=master)](https://travis-ci.org/pythological/etuples) [![Coverage Status](https://coveralls.io/repos/github/pythological/etuples/badge.svg?branch=master)](https://coveralls.io/github/pythological/etuples?branch=master) [![PyPI](https://img.shields.io/pypi/v/etuples)](https://pypi.org/project/etuples/)

Python [S-expression](https://en.wikipedia.org/wiki/S-expression) emulation using tuple-like objects.

## Examples

`etuple`s are like tuples:

```python
>>> from operator import add
>>> from etuples import etuple, etuplize

>>> et = etuple(add, 1, 2)
>>> et
ExpressionTuple((<built-in function add>, 1, 2))

>>> from IPython.lib.pretty import pprint
>>> pprint(et)
e(<function _operator.add(a, b, /)>, 1, 2)

>>> et[0:2]
ExpressionTuple((<built-in function add>, 1))
```

`etuple`s can also be evaluated:

```python
>>> et.eval_obj
3
```

Evaluated `etuple`s are cached:
```python
>>> et = etuple(add, "a", "b")
>>> et.eval_obj
'ab'

>>> et.eval_obj is et.eval_obj
True
```

Reconstructed `etuple`s and their evaluation results are preserved across tuple operations:
```python
>>> et_new = (et[0],) + et[1:]
>>> et_new is et
True
>>> et_new.eval_obj is et.eval_obj
True
```

`rator`, `rands`, and `apply` will return the operator, the operands, and apply the operation to the operands:
```python
>>> from etuples import rator, rands, apply
>>> et = etuple(add, 1, 2)

>>> rator(et)
<built-in function add>

>>> rands(et)
ExpressionTuple((1, 2))

>>> apply(rator(et), rands(et))
3
```


`rator` and `rands` are [`multipledispatch`](https://github.com/mrocklin/multipledispatch) functions that can be extended to handle arbitrary objects:
```python
from etuples.core import ExpressionTuple
from collections.abc import Sequence


class Node:
    def __init__(self, rator, rands):
        self.rator, self.rands = rator, rands

    def __eq__(self, other):
        return self.rator == other.rator and self.rands == other.rands


class Operator:
    def __init__(self, op_name):
        self.op_name = op_name

    def __call__(self, *args):
        return Node(Operator(self.op_name), args)

    def __repr__(self):
        return self.op_name

    def __eq__(self, other):
        return self.op_name == other.op_name


rands.add((Node,), lambda x: x.rands)
rator.add((Node,), lambda x: x.rator)


@apply.register(Operator, (Sequence, ExpressionTuple))
def apply_Operator(rator, rands):
    return Node(rator, rands)
```

```python
>>> mul_op, add_op = Operator("*"), Operator("+")
>>> mul_node = Node(mul_op, [1, 2])
>>> add_node = Node(add_op, [mul_node, 3])
```

`etuplize` will convert non-tuple objects into their corresponding `etuple` form:
```python
>>> et = etuplize(add_node)
>>> pprint(et)
e(+, e(*, 1, 2), 3)

>>> et.eval_obj is add_node
True
```

`etuplize` can also do shallow to object-to-`etuple` conversions:
```python
>>> et = etuplize(add_node, shallow=True)
>>> pprint(et)
e(+, <__main__.Node at 0x7f347361a080>, 3)
```

## Installation

Using `pip`:
```bash
pip install etuples
```

To install from source:
```bash
git clone git@github.com:pythological/etuples.git
cd etuples
pip install -r requirements.txt
```

Tests can be run with the provided `Makefile`:
```bash
make check
```
