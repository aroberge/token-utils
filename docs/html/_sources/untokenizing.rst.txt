About untokenizing
==================

.. admonition:: Summary

    In order to modify some source code:

    1. If possible, simply mutate the string of one or more tokens.
    2. Do **not** insert tokens: if needed, simply insert a normal string in the token stream.
    3. If you want to preserve all tab character information, use ``untokenize()``.
    4. If you don't want to set a token's string to the empty string to
       effectively remove it, and absolutely want to remove a token,
       then use ``stringify()`` instead of ``untokenize()`` to obtain a string version;
       note however that all token characters will be replaced by spaces.

Understanding the untokenizing algorithm
----------------------------------------

In the previous section, we've mentioned and shown in
a few examples how we could perform
perfect tokenize/untokenize round trips. However, if you attempt
to modify a list of tokens prior to recover a string version
using ``untokenize``, you might get some surprising result if
you try to use the same approach as that used for Python's
tokenize examples.

To understand what is going on, I will use a simple example
where I will only keep two tokens::

    >>> source = "one two three"
    >>> new_tokens = []
    >>> for token in generate_tokens(source):
    ...     if token.is_in(["one", "three"]):
    ...         new_tokens.append(token)
    ...
    >>> for token in new_tokens:
    ...     print(repr(token))
    ...
    type=1 (NAME)  string='one'  start=(1, 0)  end=(1, 3)  line='one two three'
    type=1 (NAME)  string='three'  start=(1, 8)  end=(1, 13)  line='one two three'
    >>> untokenize(new_tokens)
    'one two three'

So, we have only two tokens and yet the whole line gets reconstructed.

Note that tokens are on the same row/line (1); the first **ends at column 3**
and the second **begins at column 8**. For both tokens, the
**line attribute** contains the entire content of the original line.

.. sidebar:: Original version

    `The original version <https://github.com/myint/untokenize>`_
    created in 2013, is unmaintained and apparently
    can no longer be installed from Pypi as it is uses
    an old ``setup.py`` version.

Below is the slightly modified ``untokenize`` used in
token-utils,
based on the clever algorithm designed by Steven Mynt,
which guarantees to recover every character
initially present in the source, thus enabling a perfect
tokenize/untokenize round trip.

Other than adapting to use with token-utils tokens rather
that those coming from Python's ``tokenize`` module,
the only addition we made was to allow the insertion of
simple strings (instead of tokens) as a way to insert
content into an original source.

.. literalinclude:: ../../src/token_utils/tokenizing.py
   :language: python
   :start-after: # Begin code (for extraction by Sphinx)
   :end-before: # End code (for extraction by Sphinx)
   :linenos:
   :emphasize-lines: 12-14, 29-31, 36


Let's focus on the following for the example we just saw.

.. code-block:: none

    one two three    <-- line
    ( ).....(   )
      3     8

    ...
    if token.start_col > last_column:
        # Insert the content that was skipped between tokens
        words.append(token.line[last_column : token.start_col])
    ...

    if 8 > 3:
        words.append(line[3:8])

Now we see why ``two`` was included in the untokenized output
even though we removed the token having it as a string.

Also note:

.. code-block::

    ...
    if isinstance(token, str):
        words.append(token)
        continue

So, in order to modify the source code, there are two
ways to proceed when using ``untokenize()`` to recover modified source:

1. If possible, simply mutate the string of one or more tokens.
2. When needed, simply insert a normal string in the token stream.

Let's use the first method to show how to remove comments.

.. code-block::

    >>> from token_utils import generate_tokens, untokenize
    >>> new_tokens = []
    >>> source = """import math  # an important module
    ... print(math.pi)  # a famous constant
    ... """
    >>> print(source)
    import math  # an important module
    print(math.pi)  # a famous constant

    >>> for token in generate_tokens(source):
    ...     if token.is_comment():
    ...         token.string = ""
    ...     new_tokens.append(token)
    ...
    >>> print(untokenize(new_tokens))
    import math
    print(math.pi)

While you cannot see them, note that this ends up leaving some extra spaces
at the end of each line.

As for adding string content: remember our ``float_to_decimal()`` function?
In order to use decimals properly, we need to do the appropriate import first.
Here's a modified version:

.. literalinclude:: ../../docs_examples/decimal_tok2.py

Let's use it::

    >>> from decimal_tok2 import float_to_decimal
    >>> print(float_to_decimal("a = 1.0 + 3.0j"))
    from decimal import Decimal

    a = Decimal('1.0') + 0.0
    >>>


Inserting tokens?
------------------

What if we were to insert tokens like the example in the Python documentation.

We can create additional tokens with token-utils in a fairly simple way::

    >>> from token_utils import make_fake_token, generate_tokens, untokenize, stringify
    >>> help(make_fake_token)
    Help on function make_fake_token in module token_utils.token_class:

    make_fake_token(type=-4, string='$', start=(0, 0), end=(0, 0), line='')
        Useful when we need to process a list of tokens with
        multiple consecutive at a time ...

    >>> fake = make_fake_token(string=" | ")
    >>> tokens = []
    >>> source = "one two three"
    >>> for token in generate_tokens(source):
    ...    tokens.append(token)
    ...    if token.is_name():   # or .is_identifier() which is sligtly different
    ...        tokens.append(fake)
    ...
    >>> for token in tokens:
    ...    print(repr(token))
    ...
    type=1 (NAME)  string='one'  start=(1, 0)  end=(1, 3)  line='one two three'
    type=-4 (FAKE_TOKEN)  string=' | '  start=(0, 0)  end=(0, 0)  line=''
    type=1 (NAME)  string='two'  start=(1, 4)  end=(1, 7)  line='one two three'
    type=-4 (FAKE_TOKEN)  string=' | '  start=(0, 0)  end=(0, 0)  line=''
    type=1 (NAME)  string='three'  start=(1, 8)  end=(1, 13)  line='one two three'
    type=-4 (FAKE_TOKEN)  string=' | '  start=(0, 0)  end=(0, 0)  line=''
    type=4 (NEWLINE)  string=''  start=(1, 13)  end=(1, 14)  line='one two three'
    type=0 (ENDMARKER)  string=''  start=(2, 0)  end=(2, 0)  line=''

At first glance, this should look right: we have an alternance of ``NAME``
tokens and ``FAKE_TOKEN`` as we wanted. Let's produce a
string by untokenizing this.

    >>> untokenize(tokens)
    'one | one two | one two three | one two three'

If you go through the algorithm of the ``untokenize`` function, you will understand
why the weird-looking result is produced, and why this is definitely not recommended.

About stringify()
-----------------

``stringify()`` is nearly identical to ``untokenize()``. However, instead of having::

    ...
    if token.start_col > last_column:
        # Insert the content that was skipped between tokens
        words.append(token.line[last_column : token.start_col])
    ...

it has::

    ...
    if token.start_col > last_column and not token.is_space():
        # Insert spaces instead of the content that was skipped between tokens
        # except at the end of line before a NL or NEWLINE token
        words.append(" " * (token.start_col - last_column))
    ...

Thus, as long as one does not care about tab characters being converted into single space
characters, one can **remove** tokens safely, and their content will not be
reinserted by ``stringify()``.

``stringify()`` also has an extra parameter, ``remove_comments=False``. If sets to ``True``,
it returns a source with end of line comments removed.

Here's the result using ``stringify()``::

    >>> stringify(tokens)
    'one |     two |         three | '

While ``stringify()`` "does the right thing" when adding tokens, it is usually
preferable to simply add ordinary strings.
