Tutorial: recipes, tips, and tricks
=====================================


In what follows, I will attempt to demonstrate some useful ways to
use token-utils, focusing on those that make changes to
existing code. For simplicity, all the examples will assume
that I did ``from token_utils import *``.

.. sidebar:: Suggestions welcome

  If you can think of other useful examples,
  newer or better helper functions,
  please do not hesitate to file an issue.

Adding a factorial symbol
--------------------------

The factorial function is included in the math module.
In usual mathematical notation, we would write something like::

    n! == n * (n-1) * .... * 2 * 1

Let's see what tokens would represents a simple factorial::

    >>> print_tokens("n!")
    Extracting physical lines from source:

    type=1 (NAME)  string='n'  start=(1, 0)  end=(1, 1)  line='n!'
    type=60 (ERRORTOKEN)  string='!'  start=(1, 1)  end=(1, 2)  line='n!'
    type=4 (NEWLINE)  string=''  start=(1, 2)  end=(1, 3)  line='n!'
      --> line:  'n!'
    type=0 (ENDMARKER)  string=''  start=(2, 0)  end=(2, 0)  line=''
      --> line:  ''

While there's nothing wrong with ``!`` being an ``ERRORTOKEN`` for us,
let's nonetheless add it to the list of valid operators recognized by
Python. We will see a bit later why it is often very useful
to add symbols to the list of operators.

.. code-block::

    >>> add_operator("!", "exclamation")
    True
    >>> print_tokens("n!")
    Extracting physical lines from source:

    type=1 (NAME)  string='n'  start=(1, 0)  end=(1, 1)  line='n!'
    type=54 (OP: EXCLAMATION)  string='!'  start=(1, 1)  end=(1, 2)  line='n!'
    type=4 (NEWLINE)  string=''  start=(1, 2)  end=(1, 3)  line='n!'
      --> line:  'n!'
    type=0 (ENDMARKER)  string=''  start=(2, 0)  end=(2, 0)  line=''
      --> line:  ''
    >>> tokens = tokenize("n!")
    >>> tokens[1] == "!"
    True
    >>> tokens[1].is_operator()
    True

We can see that, not only ``!`` is a valid operator token, but it is also
recognized as such by the ``Token`` method ``is_operator()``.
The function ``add_operator()`` returned ``True``. If we were to add
a string already known to be an operator, it would return ``False``,
with no negative consequence.

.. sidebar:: '!' in Python 3.12+

    For Python 3.12+, if you use Python's ``tokenize``
    module directly, you will see that ``!``
    is defined as an operator.

While Python does not care about spaces between tokens, humans do.
For the mathematically inclined, it wouldn't be appropriate to write something
like::

    a = 3                                          !

expecting ``a`` to be now equal to 6. So, to define a factorial, we will
require ``!`` to come **immediately after** either a variable name (identifier)
or an integer; by 'immediately after', we mean no space between the two
tokens.

Here is how we can do it, using token-utils' ``immediately_after()`` instead
of ``immediately_before()`` as it looks more natural in this example.

.. literalinclude:: ../../docs_examples/factorial_1.py

Before we show it in action, we should add a word about ``pairwise``.

token-utils has its own implementation of Python's itertools function ``pairwise``
(available only for Python 3.10+). Given an iterable denoted by ``ABCDEF``,
itertools' ``pairwise`` will emit the items in pairs (tuples) like so::

    AB BC CD DE EF

Notice how the last item is never emitted as the first item of a pair.
To "solve this problem",
token-utils adds a fake token (``$``) to the iterable list so that each
token of the original sequence appears as a the first element of the pair::

    AB BC CD DE EF F$

There is also an option to have this extra token at the beginning if it
is more convenient to focus on the second element of a pair.

As for the rest of the algorithm, we assume that is should be straightforward
to understand given our description of
the problem, and with the corresponding method names
``is_immediately_before()``, ``is_identifier()``, and ``is_integer()``.
The only subtlety is when we modify ``next_.string``: we can do this as
we haven't added this token to the ``new_tokens`` list.

Here's a quick demonstration of our transformation::

    >>> from factorial_1 import make_factorial
    >>> make_factorial("3!")
    'factorial(3)'
    >>> make_factorial("a = 5!")
    'a = factorial(5)'
    >>> make_factorial("4  !")    # not immediately before/after
    '4  !'

Better factorial and BracketStack
----------------------------------

Before we describe how to improve our factorial, we make a
brief detour to introduce ``BracketStack``, a class that
keeps track of whether or not brackets, ``(), {}, []``,
are closed or unclosed in a stream. When a closing bracket is added
**as a token-utils Token**, ``BracketStack`` will return
a corresponding opening bracket if is is found, and will
return ``False`` otherwise.

Here's a sample session::

    >>> stack = BracketStack()
    >>> for token in generate_tokens(" ({[ ]}) []"):
    ...     if token.is_bracket():
    ...         other = stack.add(token)
    ...         if other:
    ...             print(other, token, stack.is_empty())
    ...
    [ ] False
    { } False
    ( ) True
    [ ] True

Going back to our factorial: in addition to appearing after
integers or variable names, the factorial symbol, ``!``,
can appear after a closing parenthesis, ``)``,
as in ``(n + 1)!``, for example.
We can modify our ``make_factorial()`` function to include
such cases, again insisting that ``!`` had to appear
immediately after a symbol, such as ``)``, in order to
mean that it is meant to indicate that it is a factorial.

In addition to keeping track of open/close brackets,
we have one more difficulty to consider. Imagine that we have something
like the following::

    A B C D E ( a b c )!

If we proceed to add tokens as we find them to a ``new_tokens`` list,
when we arrive at ``)!``, we would have to go backwards, retrieve
all the previously added tokens (``a b c``), until we find the
right open parenthesis, do the appropriate modification and add back
the extracted material. This can actually be done easily using
the function ``split_at_token()``.
Here's a modified ``make_factorial()`` that uses this.

.. literalinclude:: ../../docs_examples/factorial_2.py

Inside ``split_at_token``, we make use of the ``is_identical()`` method
to ensure that we find the correct ``(``. Note that we simply need to
modify ``matching_bracket.string`` from ``(`` to ``factorial(``.
Instead of simply showing the result of such transformations,
let me instead show it after evaluation by Python using
the **ideas** project I have already mentioned in which
this is done as an example::

    > ideas -a factorial

    The following initializing code has been executed in the Ideas console:

    from math import factorial

    Ideas Console version 0.3.12. [Python version: 3.11.9]
    ideas> 3!
    6
    ideas> 3 + (4 + 7 - 3)!
    40323
    ideas> n = 8
    ideas> (n + 1)!
    362880

Keeping track of indentation with IndentStack
---------------------------------------------

In Python, the following keywords, or soft keywords, can signal the introduction
of an indented block::

    class, def, if/elif/else, for/else, try/except/else/finally, while/else, with, match, case

For some code analysis or code modification, it might be very useful of keeping track
of such keywords when they introduce a change in indentation. When they do so, and ignoring
end of line comments, they will appear as the first non-space token
on a **logical line** terminated by a colon ``:``.
If we use token-utils' ``get_logical_lines()`` to analyze some source code, the last token
of each such line will always be a ``NEWLINE`` token, preceded by a colon.
This allowed us to define the utility class ``IndentStack``.

