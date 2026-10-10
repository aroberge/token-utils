Tutorial: recipes, tips, and tricks
=====================================

When I started working with what would become token-utils, inside both
**friendly/friendly-traceback** and **ideas**, the focus was on either
analysing or modifying a few tokens at a time. As more complex cases
were considered, I continued working on lists of tokens and developed
functions which helped identified individual tokens (``get_first()``,
``get_last()``, ``get_significant_tokens()``, etc.) and their
position in the list (``get_first_index()`` for the first "significant" token,
etc.). I developed ad-hoc methods to identify entire statements, keeping
track of open/close brackets, etc., all the while working with lists
of tokens obtained more or less in an ad-hoc way. If you have come
across token-utils before, and have followed a jupyter notebook
tutorial that I wrote, you know what I mean ...

.. sidebar:: Suggestions welcome

  If you can think of other useful examples,
  newer or better helper functions,
  **please** do not hesitate to file an issue.

The current tutorial is based on a completely different approach,
which leads to much more powerful and readable code. The key functions/classes
I came up with, and which are described in this one-page tutorial are
the following:

- ``get_logical_lines()`` which I have introduced previously. There is also the
  slightly less useful ``get_physical_lines()`` which is more or less equivalent
  to the no longer existent ``get_lines()``.

- My own implementation of ``pairwise()``, similar in spirit to ``itertools.pairwise()``.

- My own implementation of ``sliding_window()``, similar to a recipe with the same name
  found in ``itertools`` as well as the third-party package ``more_itertools``.

- ``BracketStack()``, which facilitates keeping track of matching set of
  brackets (``() {} []``).

- ``IndentStack()``, which helps to keep track of statement indentation.

- ``split_at_token()``, which is useful when changes are needed in two distant
  parts of a list of tokens.

- ``add_operator()``, which is useful for exploring potential addition to Python's syntax.

In addition, the ``Token`` class has well over 30 different methods which are very useful
to identify types of tokens (and more) in a very readable way.


In what follows, I will attempt to demonstrate how to use these functions,
using examples of modifying Python's syntax.


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
Python. When exploring potential changes to Python syntax, it can
be really useful to add new operators to the tokenizer.

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

    a = 3                                          !  # <--

expecting ``a`` to be now equal to 6. So, to define a factorial, we will
require ``!`` to come **immediately after** either a variable name (identifier)
or an integer; by 'immediately after', we mean no space between the two
tokens.

Here is how we can do it, using token-utils' ``immediately_after()`` instead
of ``immediately_before()`` as it looks more natural in this example.

.. literalinclude:: ../../docs_examples/factorial_1.py

Before we show it in action, we should add a word about ``pairwise``.

token-utils has its own implementation of Python's ``itertools.pairwise`` function.
Given an iterable denoted by ``ABCDEF``,
``itertools.pairwise`` will emit the items in pairs (tuples) like so::

    AB BC CD DE EF

Notice how the last item is never emitted as the first item of a pair, so
it might require a special treatment if we want to do something
about each individual token. To "solve this problem",
token-utils adds a fake token (``$``) to the iterable list so that each
token of the original sequence appears as a the first element of the pair::

    AB BC CD DE EF F$

This way, as we loop through the tokens, we can focus on doing "something",
and then add the first token to the stream.
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
    ...         possibly_open = stack.add(token)
    ...         if possibly_open:
    ...             print(possibly_open, token, stack.is_empty())
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

.. admonition:: Test your understanding

    Modify the code to add the capability of having a
    `double factorial. <https://en.wikipedia.org/wiki/Double_factorial>`_
    Define a new operator, ``!!``, so that you don't have to identify it
    as two consecutive ``!`` tokens but as a single token.


.. note::

    Unfortunately, using ``add_operator`` does not make it possible to choose
    any arbitrary string and have the python tokenizer recognize it as an operator.
    For example, trying to  have the string ``.=`` as a new operator will not work:
    ``.`` will still be identified as a single token. Simlarly, trying to have a word,
    like ``plus`` will not work; however, something like ``|plus`` would work.

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
This allowed us to define the utility class ``IndentStack`` which we will see in action shortly.

.. tip::

    When starting on a new project, I try to use some simple well-formatted code,
    with no comments (or semi-colons ``;`` !!) where each logical line corresponds to a physical line,
    with possibly some occasional empty lines to separate some statements.
    I then use ``get_physical_lines()``, do "something", and use ``untokenize()`` to see
    the final result. This allows me to more easily identify some potential problems.

    Later, when I want my code to be more robust, I use ``get_logical_lines()``,
    which can combine multiple physical lines into a single line, delete empty lines, etc.,
    and often use ``stringify`` instead of ``untokenize`` for more predictable results.

The example I will use is that of adding a decorator to functions, but not to methods of
a class. The code to be transformed
is the following:

.. literalinclude:: ../../docs_examples/decorator_example.txt

First, let's see how ``IndentStack()`` works, using the following program.

.. literalinclude:: ../../docs_examples/view_stack.py

The result is the following::

    > py view_stack.py
    # decorator_exemple.txt   .update() --> None    ==>  []
                              .update() --> None    ==>  []
    def f1():                 .update() --> def     ==>  [('def', (3, 0))]
        pass                  .update() --> None    ==>  [('def', (3, 0))]
                              .update() --> None    ==>  [('def', (3, 0))]
    if True:                  .update() --> if      ==>  [('if', (6, 0))]
        def f2():             .update() --> def     ==>  [('if', (6, 0)), ('def', (7, 4))]
            pass              .update() --> None    ==>  [('if', (6, 0)), ('def', (7, 4))]
    else:                     .update() --> if      ==>  [('if', (6, 0))]
        def f3():             .update() --> def     ==>  [('if', (6, 0)), ('def', (10, 4))]
            pass              .update() --> None    ==>  [('if', (6, 0)), ('def', (10, 4))]
                              .update() --> None    ==>  [('if', (6, 0)), ('def', (10, 4))]
    def f4():                 .update() --> def     ==>  [('def', (13, 0))]
        pass                  .update() --> None    ==>  [('def', (13, 0))]
                              .update() --> None    ==>  [('def', (13, 0))]
    class Something:          .update() --> class   ==>  [('class', (16, 0))]
        def method():         .update() --> def     ==>  [('class', (16, 0)), ('def', (17, 4))]
            pass              .update() --> None    ==>  [('class', (16, 0)), ('def', (17, 4))]
                              .update() --> None    ==>  [('class', (16, 0)), ('def', (17, 4))]
    if (                      .update() --> None    ==>  []
        True                  .update() --> None    ==>  []
    ):                        .update() --> None    ==>  []
        pass                  .update() --> None    ==>  []
                              .update() --> None    ==>  []

As we can see, the last ``if`` block was not correctly identified as the line on which it
appeared did not end in a colon. We could have situations, such as **inside** a comprehension,
where the code is formatted so that an ``if`` or ``for`` appears as the first token on a
physical line, and does not signal a change in indentation -- and the physical line does not end
in a colon.

Before trying to add a decorator, let's use ``get_logical_lines`` and use a method
of ``IndentStack`` to see when we are inside a ``def`` or ``class`` block.

.. literalinclude:: ../../docs_examples/inside_blocks.py

The result is the following::

    > py inside_blocks.py
    def f1():            inside_def=False; inside_class=False;   stack: [('def', (3, 0))]
        pass             inside_def=True; inside_class=False;   stack: [('def', (3, 0))]
    if True:             inside_def=False; inside_class=False;   stack: [('if', (6, 0))]
        def f2():        inside_def=False; inside_class=False;   stack: [('if', (6, 0)), ('def', (7, 4))]
            pass         inside_def=True; inside_class=False;   stack: [('if', (6, 0)), ('def', (7, 4))]
    else:                inside_def=False; inside_class=False;   stack: [('if', (6, 0))]
        def f3():        inside_def=False; inside_class=False;   stack: [('if', (6, 0)), ('def', (10, 4))]
            pass         inside_def=True; inside_class=False;   stack: [('if', (6, 0)), ('def', (10, 4))]
    def f4():            inside_def=False; inside_class=False;   stack: [('def', (13, 0))]
        pass             inside_def=True; inside_class=False;   stack: [('def', (13, 0))]
    class Something:     inside_def=False; inside_class=False;   stack: [('class', (16, 0))]
        def method():    inside_def=False; inside_class=True;   stack: [('class', (16, 0)), ('def', (17, 4))]
            pass         inside_def=True; inside_class=True;   stack: [('class', (16, 0)), ('def', (17, 4))]
    if (    True):       inside_def=False; inside_class=False;   stack: [('if', (20, 0))]
        pass             inside_def=False; inside_class=False;   stack: [('if', (20, 0))]

Note how the last ``if`` block is correctly identified, with three physical lines having
been concatenated to form a single logical line.

Adding a decorator
~~~~~~~~~~~~~~~~~~~

For our decorator example, we will want both ``f1, f2, f3, f4`` to be decorated, but not ``method``.
Here's some code to do it, followed by a brief explanation and the result.

.. literalinclude:: ../../docs_examples/add_decorator.py

If a line starts with the word ``def`` and is not inside a ``class`` indented block,
we add a line containing ``@decorator\n``, a simple string and not a list of tokens.
This extra line is added with the same indentation as the function definition,
which we obtained by doing ``" " * token.indentation()``. Here's the result of running
this script::

    > py add_decorator.py
    @decorator
    def f1():
        pass
    if True:
        @decorator
        def f2():
            pass
    else:
        @decorator
        def f3():
            pass
    @decorator
    def f4():
        pass
    class Something:
        def method():
            pass
    if (    True):
        pass

Adding a better keyword: nobreak
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both ``for`` and ``while`` loops can use an ``else`` clause which seems to
cause a bit of confusion when people see it for the first time.
Raymond Hettinger once suggested that a better keyword to use
instead might have been ``nobreak`` as it describes better that the
code in this block is intended to be run if ``break`` did not
end a loop.

Suppose we want to use ``nobreak`` appropriately, transforming it
into ``else`` prior to having it being executed by Python.
Such an example is actually available in the **ideas** project
I mentioned previously.

First, here's the code we'll modify:

.. literalinclude:: ../../docs_examples/nobreak.txt

We **don't** want to be able to use ``nobreak`` in an ``if`` block
nor in a ``try`` block, since we can't have a ``break`` statement.
We include them in this example to demonstrate how we can
selectively exclude them.
The code we use is the following:

.. literalinclude:: ../../docs_examples/nobreak.py

Unlike the previous example, we use ``untokenize()`` to get a final
result as this will include the comments in the output.
Here's the result::

    > py nobreak.py
    while True:
        pass
    else:  # <-- else
        pass
    if True:
        pass
    elif something:
        pass
    nobreak:  # keep nobreak
        error
    try:
        ...
    except:
        ...
    nobreak:  # keep nobreak
        ...
    for i in range(3):
        ...
    else:  # <-- else
        ...
    if something:
        while True:
            pass
        else:  # <-- else
            done

