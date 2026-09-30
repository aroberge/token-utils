"""
utils.py
------------------

A collection of various functions
"""

from collections import deque as _deque
from itertools import chain as _chain, islice as _islice

from token_utils.tokenizing import (
    generate_tokens as _generate_tokens,
    tokenize as _tokenize,
    untokenize as _untokenize,
)
from token_utils.token_class import make_fake_token as _make_fake_token


def pairwise(iterable, prev=0):
    """Similar to itertools.pairwise (Python 3.10+). However, it adds a fake
    token at the end if ``prev==0`` (the default) or at the beginning
    if ``prev==1``. Any other value will result in a ``ValueError``

    Given a list of tokens represented by lower case letters, and a fake token by F,
    the default corresponds to something like::

        pairwise('abcde') → Fa ab bc cd de
    """
    if prev not in [0, 1]:
        raise ValueError("'prev' must be either 0 (the default) or 1.")
    iterator = iter(iterable)
    if prev:
        updated_iterator = _chain([_make_fake_token()], iterator)
    else:
        updated_iterator = _chain(iterator, [_make_fake_token()])
    a = next(updated_iterator, None)

    for b in updated_iterator:
        yield a, b
        a = b


def sliding_window(iterable, n, prev=0):
    """Collect data into overlapping fixed-length chunks or blocks.

    This is inspired by an itertools recipe. Given an iterator,
    and a requested 'window' of size 'n', by default (prev=0),
    it adds 'n-1' fake token at the end and iterates, emitting 'n'
    items at a time until all the items have been served.

    Given a list of tokens represented by lower case letters,
    and F representing a fake token, we would have something like:

    sliding_window('abcde', 3) → abc bcd cde deF eFF

    With ``prev==1``, we would have 1 fake token prepended and
    one appended; thus

    sliding_window('abcde', 3, prev=1) → Fab abc bcd cde deF

    We must have ``0 <= prev < n``, otherwise a ValueError is raised

    We essentially have::

        sliding_window(iterable, 2) == pairwise(iterator)
    """
    if not 0 <= prev < n:
        raise ValueError(f"'prev' must be in the interval [0, {n}]")

    iterator = iter(iterable)
    fake = [_make_fake_token(string=f"FAKE_{i}") for i in range(n - 1)]
    iterator = iter(iterable)
    updated_iterator = _chain(fake[:prev], iterator, fake[prev : n - 1])

    window = _deque(_islice(updated_iterator, n - 1), maxlen=n)
    for x in updated_iterator:
        window.append(x)
        yield tuple(window)


def get_number_significant_tokens(tokens):
    """Given a list of tokens representing a single line,
    gives a count of the number of tokens which are not space tokens
    (such as ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) nor
    comments.

    If the list of tokens includes tokens from more than a single
    line, an exception is raised.
    """
    if len(tokens) == 0:
        raise ValueError("At least one token must be included in the list.")
    row = tokens[0].start_row
    nb = 0
    for token in tokens:
        if token.start_row != row:
            raise ValueError(
                "The list of tokens includes tokens from more "
                + "than one line of code."
            )
        if token.is_space() or token.is_comment():
            continue
        nb += 1
    return nb


def strip_comments(source):
    """Removes the comments in a source.

    It also removes any space at the end of each line
    (before the ``\\n`` if present).
    """
    # The untokenizing function uses not only the string attribute
    # but also the start_col, end_col, and line attributes
    # to see if any character included in the line attribute
    # between the end_col of a token preceeding the start_col
    # of another must be included. Thus, we must not simply remove
    # tokens from a stream unless they contain only spaces,
    # otherwise we might not get the desired result.
    tokens = []

    for token in _generate_tokens(source):
        if token.is_comment():
            token.string = ""  # does not remove any space preceeding it.
        tokens.append(token)

    mid_removal = _untokenize(tokens)
    # now we remove the extra spaces before the commment
    lines = mid_removal.split("\n")
    new_lines = [line.rstrip() for line in lines]
    return "\n".join(new_lines)


def dedent(tokens, nb):
    """Given a list of tokens representing a line,
    produces an equivalent list corresponding
    to a line of code with the first nb characters removed.

    If the list includes tokens from more than one line,
    or no token at all, a ``ValueError`` is raised.

    If an attempt to remove non-space characters is made,
    a ``TypeError`` is raised.

    If a negative value for nb is used, the line is indented
    by spaces or tab characters instead, with the
    first character determining if spaces or tab characters
    must be used.
    """
    # The "indent" part is probably not needed...
    if len(tokens) == 0:
        raise ValueError("Empty list of tokens was passed to dedent()/indent().")
    row = tokens[0].start_row
    for token in tokens:
        if token.start_row != row:
            raise ValueError(
                "Tokens in dedent()/indent() do not come from a single line of code."
            )
    line = _untokenize(tokens)
    if nb >= 0:
        begin = line[:nb]
        end = line[nb:]
        if begin.strip():
            raise TypeError("Attempting to remove non-space character in dedent().")
        return _tokenize(end)

    nb = -nb
    if len(line) == 0:
        return _tokenize(" " * nb)
    first_char = line[0]
    if first_char == "\t":
        line = "\t" * nb + line
    else:
        line = " " * nb + line
    return _tokenize(line)


def indent(tokens, n):
    """Calls dedent(tokens, -n) and adds the required number of spaces
    or tab characters as needed"""
    return dedent(tokens, -n)


__all__ = ["__all__"]
_names = dir()


def _make_all():
    for name in _names:
        if not name.startswith("_"):
            __all__.append(name)


_make_all()
_make_all()
__all__.remove("__all__")
