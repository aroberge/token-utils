.. sidebar::

    `Code on Github <https://github.com/aroberge/token-utils>`_

Purpose
-------

The purpose of token-utils is to simplify manipulations of tokens normally
obtained from Python's `tokenize module <https://docs.python.org/3/library/tokenize.html>`_.
One of token-utils' features is that, unlike Python's version, the following
is always guaranteed::

    from token_utils import tokenize, untokenize

    source = "Arbitrary Python code here"

    assert source == untokenize(tokenize(source))

Installation
------------

.. code-block:: none

    pip install token-utils

Example
-------

To get an idea of the simplicity of using token-utils, consider
`this example from Python's standard library <https://docs.python.org/3/library/tokenize.html#examples>`_
which substitute Decimals for floats in a string of statements,
where we changed the name of the function for greater clarity:

.. literalinclude:: ../../docs_examples/decimal_py.py


.. sidebar:: About the examples

    The files with a name as a top comment
    are found in the ``/docs_examples``
    directory of the repository.


Here's how you could achieve the same result with token-utils:

.. literalinclude:: ../../docs_examples/decimal_tok.py

.. important::

    token_utils's tokenizer is based on Python's version 3.11.
    As such, it has a limitation when it comes to parsing f-strings.

    This was done because, starting with Python 3.12, the tokenizer
    can raise an exception when it encounters expressions that are not valid Python syntax.

    As token_utils is partly intended to experiments with alternative to Python's
    syntax, we had to resort to using an older version, at the cost of not
    supporting fancy f-strings.


Quick links to topics
---------------------

.. toctree::
   :maxdepth: 2

    About tokens: Python vs token-utils <about_tokens>
    About untokenizing <untokenizing>
    Prelude to the tutorial <tutorial_prelude>
    Tutorial: recipes, tips, and tricks <tips>

.. toctree::
    :caption: API

    Token class <token_class>
    Tokenizing related methods <tokenizing_methods>

.. toctree::
    :caption: Appendix

    To do <todo>
