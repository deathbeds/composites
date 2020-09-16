# [function composition]


        if "shell" in locals():
            %config shell.testing.update False
[function composition] is the process of applying functions to functions. in procedural programming, like python, we're commonly performing function composition.

        def f(x): return x**2
        def g(x): return x/2
    
for example, `f(g(20)) and g(f(20))` are function compositions that we may commonly encounter in mathematics or python. it is important to note that function compositions are not commutative; `assert f(g(20)) != g(f(20))`.

python does have some functional qualities to it, like the `map and filter` functions. functional styles of programming are declarative, but python is designed to be imperative. 

`toolz` is a successful functional programming toolkit in python that powers many tools in scientific python. 

        >>> assert toolz.compose(g, f)(20) == g(f(20))
        >>> assert toolz.compose(f, g)(20) == f(g(20))
    
albeit, the right to left application is convention for function composition. it opposes left to right literacy conventions. `toolz` provides an api to compose functions in an opposite direction; from left to right using `toolz.compose_left`.

        >>> assert toolz.compose_left(f, g)(20) == g(f(20))
        >>> assert toolz.compose_left(g, f)(20) == f(g(20))
    
`poser` is designed for left to right function composition.

        >>> assert Pose[f][g](20) == g(f(20))
        >>> assert Pose[g][f](20) == f(g(20))

    
## composing

`poser` relies on the python data model to manipulate function compositions.

1. the primary mode of composition uses python attributes and item getters.
    
    1. `poser` is packed with {{λ(λ)[dir][len]()}} attributes that provide access to many builtin python functions.

        >>> Pose.range().len()
        λ(<built-in function len>, <function range at ...>)
    
    2. the same composition can be created using item getters. in this mode, partial arguments and keywords cannot be added like in the function above.
    
        >>> Pose[range][len]
        λ(<built-in function len>, <class 'range'>)

2. add, sub, 

        >>> toolz.compose(f, g)(20), toolz.compose(g, f)(20)
        (100.0, 200.0)
        >>> (λ+f+g)(20), (λ+g+f)(20)
        (200.0, 100.0)

        import toolz, poser

in the function compositions below, you'll notice different conformations of the functions `f and g`
for different forms of compositions. `poser` prefers a linear order of function composition more
closely aligned with how the process would be described in a recipe or literature.
    
        >>> assert (
        ...     toolz.compose(g, f)(20)
        ...     == toolz.pipe(20, f, g)
        ...     == toolz.compose_left(f, g)(20)
        ...     == (Pose[f][g])(20)
        ...     == (Pose + f + g)(20)
        ...     == (Pose >> f >> g)(20)
        ...     == Pose.pipe(f, g)(20)
        ... )

    
## Mutable composition
    
Typically, `poser` compositions created a new instance of the function with symbollic methods. That is to 
    
        F = Pose()
        >>> assert F[range] is not F
        
Appending a composition does not modify the composition in place.
    
        F[range] # does not modify F
        >>> F
        λ(<function I at ...>,)    
    
`poser` compositions are mutable when paired with the incremental python symbols.
    
        G = F[:]
        >>> assert G is not F
    
        G += range 
        G += len
        
        >>> G
        λ(<built-in function len>, <class 'range'>)
        
    

[function composition]: https://en.wikipedia.org/wiki/Function_composition
[imperative v declarative]: https://ui.dev/imperative-vs-declarative-programming/
[data model]: https://docs.python.org/3/reference/datamodel.html
[expressions]: https://docs.python.org/3/reference/expressions.html
    
        (__annotations__['data model'])
 