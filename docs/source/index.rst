
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
which substitute Decimals for floats in a string of statements::

    from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
    from io import BytesIO

    def decistmt(s):
        result = []
        g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, tokval, _, _, _ in g:
            if toknum == NUMBER and '.' in tokval:  # replace NUMBER tokens
                result.extend([
                    (NAME, 'Decimal'),
                    (OP, '('),
                    (STRING, repr(tokval)),
                    (OP, ')')
                ])
            else:
                result.append((toknum, tokval))
        return untokenize(result).decode('utf-8')


Here's how you could achieve the same result with token-utils::

    from token_utils import tokenize, untokenize

    def decistmt(source):
        tokens = tokenize(source)
        for token in tokens:
            if token.is_float():
                token.string = f"Decimal('{token.string}')"
        return untokenize(tokens)


Quick links to topics
---------------------

.. sidebar:: Work in progress

    Much more content will be added ... *soon*.


.. toctree::
   :maxdepth: 2

    About tokens and token-utils <about_tokens>
    API <api>


.. toctree::
    :caption: Appendix

    Origin and history of token-utils <history>
    Tokenizing notebook <tokenize_notebook>



To do
-----

.. todolist::



