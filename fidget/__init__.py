# coding: utf-8

try:
    from .sequence import _s, _l, _t, _list_, _tuple_, _set_, _sequence_
    from .container import _d, _f, _dict_, _condition_
    from .composite import _x, stars, _comp_, _pmoc_, x_
    from .chain import _this_, _self_
    from .recipes import functor, juxt
except:
    from sequence import _s, _l, _t, _list_, _tuple_, _set_, _sequence_
    from container import _d, _f, _dict_, _condition_
    from composite import _x, stars, _comp_, _pmoc_, x_
    from chain import _this_, _self_
    from recipes import functor, juxt


__all__ = [
    '_x', 'x_', '_s', '_d', '_l', '_t', '_f', 'stars', '_comp_', '_pmoc_',
    '_dict_', '_list_', '_condition_', '_set_', '_tuple_', '_this_', '_self_',
    '_sequence_', 'functor', 'juxt'
]


from toolz.curried.operator import *
import toolz.curried.operator
from toolz.curried import *
import toolz.curried
from copy import copy


not_private = complement(compose(eq('_'), first))

__all__ = list(
    concatv(
        filter(not_private, dir(toolz.curried)),
        filter(not_private, dir(toolz.curried.operator)), ['copy'], __all__))

