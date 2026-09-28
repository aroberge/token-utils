
token-utils
========================================================

`Code on Github <https://github.com/aroberge/token-utils>`_

Installation
------------

.. code-block:: none

    pip install token-utils

Purpose
-------

The purpose of token-utils is to simplify manipulations of tokens normally
obtaind from Python's `tokenize module <https://docs.python.org/3/library/tokenize.html>`_.
One of token-utils' features is that, unlike Python's version, the following
is always guaranteed::

    from token_utils import tokenize, untokenize

    source = "Arbitrary Python code here"

    assert source == untokenize(tokenize(source))


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


Quick links to topics
---------------------

.. sidebar:: Work in progress

    Much more content will be added ... *soon*.


.. toctree::
   :maxdepth: 2

    About tokens: Python vs token-utils <about_tokens>
    About untokenizing <untokenizing>
    API <api>


.. toctree::
    :caption: Appendix

    Origin and history of token-utils <history>



To do
-----

.. todolist::



