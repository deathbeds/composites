
# coding: utf-8

__test__ = dict(
    gold="""
    >>> g = a**str*[[str.upper]]|a**int*range|a**float*type
    >>> f = a/g*list
    >>> assert f(['keep it 💯', 10, 10.]) == [[["KEEP IT 💯"]], range(10), float]
    >>> assert copy(g).type()({}) is Ø""",
    simple=""">>> assert simple[range](10) == range(10)
    >>> assert simple[range][type](10) is range
    >>> assert simple[range][type][type](10) is type

    Begin a composition with a decorator.
    >>> @simple.append
    ... def thang(x):
    ...     return range(x)
    >>> assert thang[len](10) is 10""",
    juxt="""
    >>> assert juxt[range](10) == [range(10)]
    >>> assert juxt[range][type](10) == [range(10), int]
    >>> assert juxt[range][type][str](10) == [range(10), int, '10']

    Create a juxtaposable object `model`.
    >>> @juxt.append
    ... def model(x): return range(x)

    Append more functions to the `model`
    >>> @model.append
    ... def _(x): return type(x)

    >>> assert isinstance(Juxtaposition({})(), dict) and isinstance(Juxtaposition([])(), list) and isinstance(Juxtaposition(tuple())(), tuple)""")


# # Complex Composite Functions
#
# Complex composite functions have real and imaginary parts that may except specific errors.
#
# ## Composition
#
# Composite functions use Python syntax to append callable objects to compositions and juxtapositions.
#
# ### Operator

from functools import partialmethod, wraps, partial
import sys
import operator
import inspect
from collections import Sized, Mapping, Iterable
from toolz import excepts, complement, concat, reduce, groupby
from copy import copy

dunder = '__{}__'.format

__all__ = 'a', 'an', 'the', 'simple', 'flip', 'parallel', 'star', 'do', 'preview', 'x', 'op', 'juxt', 'cache', 'store', 'Ø', 'Composition', 'Operation', 'Juxtaposition', 'Proposition', 'Exposition', 'Imposition'


def isiterable(object): return isinstance(object, Iterable)


binop = 'add', 'sub', 'mul', 'truediv', 'floordiv', 'mod', 'lshift', 'rshift'
boolop = 'gt', 'ge', 'le', 'lt', 'eq', 'ne'
nop = 'abs', 'pos', 'neg', 'pow'


# Composing function strictly through the Python datamodel.

def call(object, *tuple, Exception=None, **dict):
    """Call the object with an argument tuple, a keyword dict, and E

    >>> assert call(10) is 10
    >>> assert call(range, 10, 20) == range(10, 20)"""
    return (
        Exception and excepts(Exception, object, identity) or object
    )(*tuple, **dict) if callable(object) else object


def identity(*tuple, **dict):
    """A identity function that returns the first arguments if it exists.

    >>> assert not identity(**dict(foo=42))
    >>> assert identity(10, 20, dict(foo=42)) is 10
    """
    return tuple[0] if tuple else None


class This(partial):
    """Supply partial arguments to objects.

    >>> assert This(str.replace, 'a', 'b')('abc') == 'bbc'
    """
    def __call__(x, object): return x.func(object, *x.args, **x.keywords)


class State:
    """State attributes for pickling and copying propositions."""

    def __hash__(x): return hash(map(hash, x))

    def __getstate__(x):
        return tuple(getattr(x, slot, None) for slot in x.__slots__)

    def __setstate__(x, tuple):
        return list(
            setattr(x, str, object) for str, object in zip(x.__slots__, tuple)
        ) and x

    @property
    def __name__(x): return type(x).__name__

    __signature__ = inspect.signature(identity)


class flip(State):
    """Flip the argument of a callable.

    >>> assert flip(range)(20, 10) == range(10, 20)
    """
    __slots__ = 'callable',

    def __init__(x, callable): x.callable = callable

    def __call__(x, *tuple, **dict): return call(x.callable,
                                                 *reversed(tuple), **dict)


class Outer(State):
    __slots__ = 'callable',

    def __init__(x, object=None):
        x.callable = list() if object is None else object

    def __iter__(x):
        # Juxt is defined way later on unfortunately, but this is the most
        # efficient place.
        yield from map(
            Juxt, dict.items(x.callable) if isinstance(x.callable, dict) else x.callable)

    def __call__(x, *tuple, **dict):
        for callable in x:
            tuple, dict = (call(callable, *tuple, **dict),), {}
        return identity(*tuple, **dict)

    def __len__(x): return isinstance(
        x.callable, Sized) and len(
        x.callable) or 0

    def __repr__(x): return repr(x.callable)

    def __bool__(x): return bool(len(x))


class Inner(Outer):
    def __iter__(x): yield from x.callable and super().__iter__() or (True,)

    def __call__(x, *tuple, **dict):
        return super().__call__(*tuple, **dict) or Ø(x.callable)


class Ø(BaseException):
    """An Inner callable may return a Ø Exception."""
    def __bool__(x): return False

    def __invert__(x): return True


def _is_isinstance(object):
    """Prepare types and types as isinstance functions.

    >>> assert _is_isinstance(int)(10) and not _is_isinstance(int)('10')
    """
    if isinstance(object, type) and object is not bool:
        object = object,
    if isinstance(object, tuple):
        object = This(isinstance, object)
    return object


class Pose(State):
    """Pose a complex function with Inner and Outer callable. The Outer callable may accept exceptions.
    Pose is combined with the prefixes Pro, Ex, Im, and Juxt to evaluate inner call methods.
    """
    __slots__ = 'Inner', 'Outer', 'Exception'
    _repr_token_ = '^'

    def __init__(x, inner=None, outer=None, *, exception=None):
        inner = _is_isinstance(inner)

        for name in ('inner', 'outer'):
            object = locals().get(name)
            if object is not None and not isiterable(
                    object) or isinstance(object, Pose):
                locals()[name] = [object]

        x.Inner, x.Outer, x.Exception = Inner(inner), Outer(outer), exception

    def __bool__(x): return bool(x.Outer)

    def __repr__(x): return x._repr_token_.join(map(repr, (x.Inner, x.Outer)))

    def __call__(x, *tuple, **dict):
        return call(
            x.Outer,
            *tuple,
            **dict,
            Exception=dict.pop(
                'Exception',
                x.Exception))


class Juxt(Pose):
    """Juxtapose arguments cross callables."""
    def __new__(x, object=None, **dict):
        """Juxtapose is used generically to iterate through Sequences and Mappings. The
        new method returns callables and initializes everything else.  When called, Juxt
        will return an object with the same type as Juxt.Outer.
        """
        if callable(object):
            return object
        if object is None:
            object = list()
        if isiterable(object) and not isinstance(object, str):
            x = super().__new__(x)
            return x.__init__(**dict) or x
        return object

    def __init__(x, outer=None, **dict): super().__init__(outer=outer, **dict)

    def __call__(x, *args, **kwargs):
        return (
            type(
                x.Outer.callable) if isinstance(
                x.Outer.callable,
                Sized) else identity)(
            call(
                callable,
                *
                args,
                **kwargs) for callable in x.Outer)


# # Composites

class Pro(Pose):
    """Propose a ~Ø inner condition then evaluate the outer function."""
    def __call__(x, *tuple, **dict):
        object = x.Inner(*tuple, **dict)
        if x.Outer:
            return object if isinstance(
                object, Ø) else super().__call__(
                *tuple, **dict)
        # If there is not outer function return a boolean.
        return object


class Ex(Pose):
    """Pipe ~Ø inner return values to the outer callable."""
    _repr_token_ = '&'

    def __call__(x, *tuple, **dict):
        object = x.Inner(*tuple, **dict)
        if object is True:
            object = identity(*tuple, **dict)
        return object if isinstance(object, Ø) else super().__call__(object)


class Im(Pose):
    """If the inner function is Ø evaluate the outer function."""
    _repr_token_ = '|'

    def __call__(x, *tuple, **dict):
        object = x.Inner(*tuple, **dict)
        if object is True:
            object = identity(*tuple, **dict)
        return super().__call__(*tuple, **dict) if isinstance(object, Ø) else object


class Λ:
    def append(x, object): return x().append(object)

    def __bool__(x): return False


def _inner_(x): return [] if isinstance(x, Λ) else [x]


class Conditions:
    # Lambda initializes propositions.
    # The [*]positions are defined later.
    def __pow__(x, object): return Proposition(
        inner=_inner_(x) + [_is_isinstance(object)])

    def __and__(x, object): return Exposition(inner=_inner_(x), outer=[object])

    def __or__(x, object): return Imposition(inner=_inner_(x), outer=[object])

    def __xor__(x, object): return setattr(x, 'exceptions', object) or x

    then = __and__
    ifnot = __or__
    instance = ifthen = __pow__
    excepts = __xor__


class __getattr__(object):
    def __init__(x, object, next=None):
        x.object, x.next = object, next

    def __getattr__(x, next):
        object = x.next
        # Convert the attribute to a callable.
        if x.next:
            next = getattr(x.next, next)

        if next in sys.modules:
            next = sys.modules.get(next)

        elif isinstance(next, str):
            for module in map(__import__, Attributes.shortcuts):
                if hasattr(module, next):
                    next = getattr(module, next)
                    break
            else:
                raise AttributeError(next)

        # Decorate the discovered attribute with the correct partials or call.
        wrapper = False

        for decorator, set in Attributes.decorators.items():
            if next in set:
                next = partial(decorator, next)
                break
        else:
            if callable(next) and not isinstance(next, type):
                wrapper = wraps(next)
                next = partial(
                    isinstance(
                        object,
                        type) and This or partial,
                    next)

        # Wrap the new object for interaction
        next = __getattr__(x.object, next)
        return wrapper(next) if wrapper else next

    def __call__(x, *tuple, **dict):
        object = x.next
        return x.object.append(object(*tuple,
                                      **dict) if isinstance(object,
                                                            partial) else partial(object,
                                                                                  *tuple,
                                                                                  **dict) if tuple or dict else object)

    def __repr__(x):
        return repr(isinstance(x.next, partial)
                    and x.next.args and x.next.args[0] or x.next)

    def __dir__(x):
        if not x.next or isinstance(x, Attributes):
            base = (
                list(filter(This(complement(str.__contains__), '.'), sys.modules.keys()))
                + list(concat(dir(__import__(module)) for module in Attributes.shortcuts)))
        else:
            base = dir(x.next)
        return super().__dir__() + base


class Attributes:
    """
    >>> assert not any(x in dir(x) for x in sys.modules if not '.' in x)
    >>> assert all(x in dir(a) for x in sys.modules if not '.' in x)
    """
    shortcuts = 'statistics', 'toolz', 'requests', 'builtins', 'json', 'pickle', 'io', 'collections', 'itertools', 'functools', 'pathlib', 'importlib', 'inspect', 'operator'
    decorators = dict()

    def __getattr__(x, attr):
        """Access attributes from sys.modules or x.shortcuts"""
        return __getattr__(x).__getattr__(attr)

    def __dir__(x): return dir(__getattr__(x))


Attributes.decorators[This] = [__import__('fnmatch').fnmatch]
Attributes.decorators[call] = operator.attrgetter(
    'attrgetter', 'itemgetter', 'methodcaller')(operator)
Attributes.decorators[This] += [item for item in vars(
    operator).values() if item not in Attributes.decorators[call]]


class Append:
    def append(x, object): return x.Outer.callable.append(object) or x

    def __getitem__(x, object): return x.append(object)


class Symbols:
    """Operations that operator on containers.

    >>> assert a@range == a.groupby(range)
    >>> assert a/range == a.map(range)
    >>> assert a//range == a.filter(range)
    >>> assert a%range == a.reduce(range)
    >>> assert copy(a%range) == a.reduce(range)
    """
    def _left(x, callable, object=None, partial=This):
        return x.append(
            callable if object is None else partial(
                callable, Juxtaposition(object)))

    def _right(right, attr, left):
        return getattr(Symbols._left(Proposition(), left), dunder(attr))(right)

    __truediv__ = map = partialmethod(_left, map, partial=partial)
    __floordiv__ = filter = partialmethod(_left, filter, partial=partial)
    __mod__ = reduce = partialmethod(_left, reduce, partial=partial)
    __matmul__ = groupby = partialmethod(_left, groupby, partial=partial)
    __add__ = __mul__ = __sub__ = __rshift__ = Append.__getitem__

    def __lshift__(x, object): return x.append(Do(object))
    do = __lshift__


list(
    setattr(
        Symbols,
        '__r' +
        dunder(attr).lstrip('__'),
        partialmethod(
            Symbols._right,
            attr)) for attr in binop)


# # Juxtapositions

class Position(Append, Conditions, Attributes, Symbols):
    """Composition methods for establishing Positions using __magic__ Python methods.
    """


class Proposition(Pro, Position):
    """Evaluate the outer callable if the inner callable is ~Ø."""


class Exposition(Ex, Position):
    """Pass ~Ø inner function return values as input to the outer function."""


class Imposition(Im, Position):
    """Evaluate the other outer function is the inner function is Ø."""


class Juxtaposition(Juxt, Position):
    """Pass arguments to all callables in all iterables."""


IfThen, IfNot = Exposition, Imposition


class Composition(Λ, Proposition):
    def append(x, object):
        tuple, dict = getattr(x, 'args', []), getattr(x, 'kwargs', {})
        return super().append(partial(object, *tuple, **dict) if tuple or dict else object)

    __slots__ = Pose.__slots__ + ('args', 'kwargs')


class Simple(Composition):
    def __call__(x, *tuple, **dict):
        if tuple or dict:
            x = copy(x)
            x.args, x.kwargs = tuple, dict
            return x
        return super().__call__(dict.get('inner', None), *tuple, **dict)


composite = compositon = Composition(outer=[Proposition])
a = an = the = simple = λ = Simple(outer=[Proposition])
juxt = juxtaposition = Simple(outer=[Juxtaposition])


class Operate(Proposition):
    __wrapped__ = None
    __annotations__ = {}

    def __init__(x, *args, **kwargs):
        super().__init__(*args, **kwargs)
        x.__qualname__ = '.'.join((__name__, type(x).__name__))

    def _left(x, callable, arg=None, partial=This):
        return x.append(partial(callable, arg))

    def _right(x, callable, left):
        return Operate._left(Operate(), callable, left, partial=partial)

    def _bool(x, callable, *args):
        return Operate(inner=[This(callable, *args)], outer=_inner_(x))


Operate.__getattr__ = partialmethod(Operate._left, getattr)


for attr in binop + ('getitem',):
    op, rop = getattr(operator, attr), '__r' + dunder(attr).lstrip('__')
    setattr(Operate, dunder(attr), partialmethod(Operate._left, op))
    setattr(Operate, rop, partialmethod(Operate._right, op))

list(
    setattr(
        Operate,
        dunder(attr),
        partialmethod(
            Operate._bool,
            getattr(
                operator,
                attr))) for attr in boolop)
list(
    setattr(
        Operate,
        dunder(attr),
        partialmethod(
            Operate._left,
            getattr(
                operator,
                attr))) for attr in nop)


class Operation(Λ, Operate):
    """"""


x = op = Operation(outer=[Operate])


class Star(Proposition):
    _repr_token_ = "*"

    def __call__(x, object, *tuple, **dict):
        if isinstance(object, Mapping):
            return super().__call__(*tuple, **(dict.update(object) or dict))
        return super().__call__(*object, *tuple, **dict)


star = Simple(outer=[Star])


class Do(Proposition):
    _repr_token_ = '>>'

    def __call__(x, *tuple, **dict):
        super().__call__(*tuple, **dict)
        return identity(*tuple, **dict)


do = Simple(outer=[Do])


class Preview(Proposition):
    """Eager proposition evaluation."""
    def __repr__(x): return repr(x())


preview = Simple(outer=[Preview])


class parallel(Proposition):
    """An embarassingly parallel proposition.

    >>> import joblib
    >>> def g(x): return x+10
    >>> assert parallel(4).range().map(x+10)(100)
    >>> assert parallel(4).range().map(a[range])(100)
    """
    _repr_token_ = '||'

    def __init__(x, jobs=4, *tuple, **dict):
        x.jobs = jobs
        super().__init__(*tuple, **dict)

    def map(x, object): return super().map(
        __import__('joblib').delayed(object))

    def __call__(x, *tuple, **dict):
        return __import__('joblib').Parallel(
            x.jobs)(
            super().__call__(
                *tuple,
                **dict))

    __truediv__ = map


class store(dict):
    @property
    def __self__(x): return x.__call__.__self__

    def __init__(x, callable=None, *tuple, **dict):
        x.callable = Proposition(
            *tuple, **dict) if callable is None else callable
        super().__init__(*tuple, **dict)

    def __call__(x, *tuple, **dict):
        x[tuple[0]] = x.callable(*tuple, **dict)
        return x[tuple[0]]


class cache(store):
    def __call__(x, *tuple, **dict):
        if tuple[0] not in x:
            return super().__call__(*tuple, **dict)
        return x[tuple[0]]


# # Developer

if __name__ == '__main__':
    if 'runtime' in sys.argv[-1]:
        from IPython import get_ipython, display
        get_ipython().system(
            'jupyter nbconvert --to python --TemplateExporter.exclude_input_prompt=True composites.ipynb')
        # Juxtaposition still wont work
        get_ipython().system('python -m pydoc -w composites')
        get_ipython().system('pyreverse -o png -pcomposites -fALL composites')
        display.display(
            display.Image('classes_composites.png'),
            display.IFrame(
                'composites.html',
                height=600,
                width=800))
        __import__('doctest').testmod()
        get_ipython().system('ipython -m doctest  composites.py')
        get_ipython().system('python -m pydoc -w composites')

        get_ipython().system('autopep8 --in-place --aggressive --aggressive composites.py')
        get_ipython().system('flake8 composites.py --ignore E501,E704,W503')
    else:
        print('run from cli')
