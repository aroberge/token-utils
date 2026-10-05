Useful functions to know before the tutorial
=============================================

.. admonition:: Summary

  We explain briefly how token-utils makes it easy to
  work with either *physical lines* or *logical lines*
  and introduce a function, ``print_tokens``, that facilitates
  exploring tokens in an interactive session and introduce
  ``get_physical_lines()`` and ``get_logical_lines()``.

To **simplify** the information found in Python's documentation
`Lexical analysis: line structure <https://docs.python.org/3/reference/lexical_analysis.html#line-structure>`_
we can think of a Python source as consisting of:

- Physical lines, separated by newline characters; or
- Logical lines, corresponding to statements.

We've already seen how ``tokenize()`` produces a list of tokens and how we can
print those. To facilitate doing this in interactive sessions,
token-utils includes a function named ``print_tokens``.
Consider the following source::

    >>> source = """
    ... def double(
    ...       n):   # a useful function
    ...     return 2*n
    ...
    ... four = double(2)
    ... """
    >>> print_tokens(tokenize(source))
    Processing list of tokens:

    type=62 (NL)  string='\n'  start=(1, 0)  end=(1, 1)  line='\n'
    --> line:  '\n'
    type=1 (NAME)  string='def'  start=(2, 0)  end=(2, 3)  line='def double( \n'
    type=1 (NAME)  string='double'  start=(2, 4)  end=(2, 10)  line='def double( \n'
    type=54 (OP: LPAR)  string='('  start=(2, 10)  end=(2, 11)  line='def double( \n'
    type=62 (NL)  string='\n'  start=(2, 12)  end=(2, 13)  line='def double( \n'
    --> line:  'def double(\n'
    type=1 (NAME)  string='n'  start=(3, 6)  end=(3, 7)  line='      n):  <...> tion\n'
    type=54 (OP: RPAR)  string=')'  start=(3, 7)  end=(3, 8)  line='      n):  <...> tion\n'
    type=54 (OP: COLON)  string=':'  start=(3, 8)  end=(3, 9)  line='      n):  <...> tion\n'
    type=61 (COMMENT)  string='# a useful function'  start=(3, 12)  end=(3, 31)  line='      n):  <...> tion\n'
    type=4 (NEWLINE)  string='\n'  start=(3, 31)  end=(3, 32)  line='      n):  <...> tion\n'
    --> line:  '      n):   # a useful function\n'
    type=5 (INDENT)  string='    '  start=(4, 0)  end=(4, 4)  line='    return 2*n\n'
    type=1 (NAME)  string='return'  start=(4, 4)  end=(4, 10)  line='    return 2*n\n'
    type=2 (NUMBER)  string='2'  start=(4, 11)  end=(4, 12)  line='    return 2*n\n'
    type=54 (OP: STAR)  string='*'  start=(4, 12)  end=(4, 13)  line='    return 2*n\n'
    type=1 (NAME)  string='n'  start=(4, 13)  end=(4, 14)  line='    return 2*n\n'
    type=4 (NEWLINE)  string='\n'  start=(4, 14)  end=(4, 15)  line='    return 2*n\n'
    --> line:  '    return 2*n\n'
    type=62 (NL)  string='\n'  start=(5, 0)  end=(5, 1)  line='\n'
    --> line:  '\n'
    type=6 (DEDENT)  string=''  start=(6, 0)  end=(6, 0)  line='four = double(2)\n'
    type=1 (NAME)  string='four'  start=(6, 0)  end=(6, 4)  line='four = double(2)\n'
    type=54 (OP: EQUAL)  string='='  start=(6, 5)  end=(6, 6)  line='four = double(2)\n'
    type=1 (NAME)  string='double'  start=(6, 7)  end=(6, 13)  line='four = double(2)\n'
    type=54 (OP: LPAR)  string='('  start=(6, 13)  end=(6, 14)  line='four = double(2)\n'
    type=2 (NUMBER)  string='2'  start=(6, 14)  end=(6, 15)  line='four = double(2)\n'
    type=54 (OP: RPAR)  string=')'  start=(6, 15)  end=(6, 16)  line='four = double(2)\n'
    type=4 (NEWLINE)  string='\n'  start=(6, 16)  end=(6, 17)  line='four = double(2)\n'
    --> line:  'four = double(2)\n'
    type=0 (ENDMARKER)  string=''  start=(7, 0)  end=(7, 0)  line=''
    --> line:  ''


We can see how ``print_tokens`` prints a representation of each token, breaking out
the output in physical lines, with a string representation at the end.
This turns out to simply being the content of the ``line`` attribute of the tokens --
but this might not always be the case if tokens have been removed or modified
prior to printing.

We can also use this function directly on the original source::

    >>> print_tokens(source)
    Extracting physical lines from source:

    type=62 (NL)  string='\n'  start=(1, 0)  end=(1, 1)  line='\n'
    --> line:  '\n'
    type=1 (NAME)  string='def'  start=(2, 0)  end=(2, 3)  line='def double( \n'
    type=1 (NAME)  string='double'  start=(2, 4)  end=(2, 10)  line='def double( \n'
    type=54 (OP: LPAR)  string='('  start=(2, 10)  end=(2, 11)  line='def double( \n'
    type=62 (NL)  string='\n'  start=(2, 12)  end=(2, 13)  line='def double( \n'
    --> line:  'def double(\n'
    type=1 (NAME)  string='n'  start=(3, 6)  end=(3, 7)  line='      n):  <...> tion\n'
    type=54 (OP: RPAR)  string=')'  start=(3, 7)  end=(3, 8)  line='      n):  <...> tion\n'
    type=54 (OP: COLON)  string=':'  start=(3, 8)  end=(3, 9)  line='      n):  <...> tion\n'
    type=4 (NEWLINE)  string='\n'  start=(3, 31)  end=(3, 32)  line='      n):  <...> tion\n'
    --> line:  '      n):\n'
    type=1 (NAME)  string='return'  start=(4, 4)  end=(4, 10)  line='    return 2*n\n'
    type=2 (NUMBER)  string='2'  start=(4, 11)  end=(4, 12)  line='    return 2*n\n'
    type=54 (OP: STAR)  string='*'  start=(4, 12)  end=(4, 13)  line='    return 2*n\n'
    type=1 (NAME)  string='n'  start=(4, 13)  end=(4, 14)  line='    return 2*n\n'
    type=4 (NEWLINE)  string='\n'  start=(4, 14)  end=(4, 15)  line='    return 2*n\n'
    --> line:  '    return 2*n\n'
    type=62 (NL)  string='\n'  start=(5, 0)  end=(5, 1)  line='\n'
    --> line:  '\n'
    type=1 (NAME)  string='four'  start=(6, 0)  end=(6, 4)  line='four = double(2)\n'
    type=54 (OP: EQUAL)  string='='  start=(6, 5)  end=(6, 6)  line='four = double(2)\n'
    type=1 (NAME)  string='double'  start=(6, 7)  end=(6, 13)  line='four = double(2)\n'
    type=54 (OP: LPAR)  string='('  start=(6, 13)  end=(6, 14)  line='four = double(2)\n'
    type=2 (NUMBER)  string='2'  start=(6, 14)  end=(6, 15)  line='four = double(2)\n'
    type=54 (OP: RPAR)  string=')'  start=(6, 15)  end=(6, 16)  line='four = double(2)\n'
    type=4 (NEWLINE)  string='\n'  start=(6, 16)  end=(6, 17)  line='four = double(2)\n'
    --> line:  'four = double(2)\n'
    type=0 (ENDMARKER)  string=''  start=(7, 0)  end=(7, 0)  line=''
    --> line:  ''

This gives a slightly reduced output, as the ``INDENT`` and ``DEDENT`` tokens
have been removed, as well as the comment. This output is equivalent to doing
``print_tokens(get_physical_lines(source))``. Both this output, and the previous
one using the list of tokens include empty lines.

Finally, we can focus on logical lines::

    >>> print_tokens(get_logical_lines(source))
    Processing list of lists of tokens:

    type=1 (NAME)  string='def'  start=(2, 0)  end=(2, 3)  line='def double( \n'
    type=1 (NAME)  string='double'  start=(2, 4)  end=(2, 10)  line='def double( \n'
    type=54 (OP: LPAR)  string='('  start=(2, 10)  end=(2, 11)  line='def double( \n'
    type=1 (NAME)  string='n'  start=(3, 6)  end=(3, 7)  line='      n):  <...> tion\n'
    type=54 (OP: RPAR)  string=')'  start=(3, 7)  end=(3, 8)  line='      n):  <...> tion\n'
    type=54 (OP: COLON)  string=':'  start=(3, 8)  end=(3, 9)  line='      n):  <...> tion\n'
    type=4 (NEWLINE)  string='\n'  start=(3, 31)  end=(3, 32)  line='      n):  <...> tion\n'
    --> line:  'def double(      n):\n'
    type=1 (NAME)  string='return'  start=(4, 4)  end=(4, 10)  line='    return 2*n\n'
    type=2 (NUMBER)  string='2'  start=(4, 11)  end=(4, 12)  line='    return 2*n\n'
    type=54 (OP: STAR)  string='*'  start=(4, 12)  end=(4, 13)  line='    return 2*n\n'
    type=1 (NAME)  string='n'  start=(4, 13)  end=(4, 14)  line='    return 2*n\n'
    type=4 (NEWLINE)  string='\n'  start=(4, 14)  end=(4, 15)  line='    return 2*n\n'
    --> line:  '    return 2*n\n'
    type=1 (NAME)  string='four'  start=(6, 0)  end=(6, 4)  line='four = double(2)\n'
    type=54 (OP: EQUAL)  string='='  start=(6, 5)  end=(6, 6)  line='four = double(2)\n'
    type=1 (NAME)  string='double'  start=(6, 7)  end=(6, 13)  line='four = double(2)\n'
    type=54 (OP: LPAR)  string='('  start=(6, 13)  end=(6, 14)  line='four = double(2)\n'
    type=2 (NUMBER)  string='2'  start=(6, 14)  end=(6, 15)  line='four = double(2)\n'
    type=54 (OP: RPAR)  string=')'  start=(6, 15)  end=(6, 16)  line='four = double(2)\n'
    type=4 (NEWLINE)  string='\n'  start=(6, 16)  end=(6, 17)  line='four = double(2)\n'
    --> line:  'four = double(2)\n'

This does not include any empty lines, nor any ``INDENT/DEDENT/NL/COMMENT`` tokens.
Notice how the first logical line,
``def double(      n):\n``, combines two physical lines.
``get_logical_lines()`` will often be the preferable way to obtain relevant tokens
for either code analysis or code transformation.

Note that, in this specific example, doing ``untokenize(get_logical_lines(source))`` would not recover
the original source, but one functionnally equivalent.
