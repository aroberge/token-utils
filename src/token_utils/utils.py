"""
utils.py
------------------

A collection of various functions
"""

import warnings
from collections import deque
from itertools import chain, islice

from token_utils.tokenizing import tokenize, untokenize
from token_utils.token_class import make_fake_token


class TokenUtilsDeprecationWarning(DeprecationWarning):
    """Raised when deprecated function is called."""

    pass


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
        updated_iterator = chain([make_fake_token()], iterator)
    else:
        updated_iterator = chain(iterator, [make_fake_token()])
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
    fake = [make_fake_token(string=f"FAKE_{i}") for i in range(n - 1)]
    iterator = iter(iterable)
    updated_iterator = chain(fake[:prev], iterator, fake[prev : n - 1])

    window = deque(islice(updated_iterator, n - 1), maxlen=n)
    for x in updated_iterator:
        window.append(x)
        yield tuple(window)


def get_first(tokens, exclude_comment=True):
    """DEPRECATED

    Given a list of tokens, find the first token which is not a space token
    (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) and,
    by default, also not a ``COMMMENT``.

    ``COMMMENT`` tokens can be included by setting ``exclude_comment`` to ``False``.

    Returns ``None`` if none is found.
    """
    warnings.warn(
        "get_first() will soon be removed. Replace by getting a list of significant tokens",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    for token in tokens:
        if token.is_space() or (exclude_comment and token.is_comment()):
            continue
        return token
    return None


def get_first_index(tokens, exclude_comment=True):
    """DEPRECATED

    Given a list of tokens, find the index of the first token which is
    not a space token (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) nor
    a ``COMMMENT``. If it is desired to include COMMENT, set ``exclude_comment``
    to ``True``.

    Returns ``None`` if none is found.
    """
    warnings.warn(
        "get_first_index() will soon be removed. Replace by getting a list of significant tokens",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    for index, token in enumerate(tokens):
        if token.is_space() or (exclude_comment and token.is_comment()):
            continue
        return index
    return None


def get_last(tokens, exclude_comment=True):
    """DEPRECATED

    Given a list of tokens, find the last token which is not a space token
    (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) and, by default,
    also not a ``COMMMENT``.

    ``COMMMENT`` tokens can be included by setting``exclude_comment``
    to ``False``.

    Returns ``None`` if none is found.
    """
    warnings.warn(
        "get_last() will soon be removed. Replace by getting a list of significant tokens",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    return get_first(reversed(tokens), exclude_comment=exclude_comment)


def get_last_index(tokens, exclude_comment=True):
    """DEPRECATED

    Given a list of tokens, find the index of the last token which is
    not a space token (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) nor
    a ``COMMMENT``. If it is desired to include COMMENT, set ``exclude_comment``
    to True.

    Returns ``None`` if none is found.
    """
    warnings.warn(
        "get_first_index() will soon be removed. Replace by getting a list of significant tokens",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    return (
        len(tokens)
        - 1
        - get_first_index(reversed(tokens), exclude_comment=exclude_comment)
    )


def get_number(tokens, exclude_comment=True):
    """DEPRECATED

    Given a list of tokens, gives a count of the number of
    tokens which are not space tokens (such as ``NEWLINE``, ``INDENT``,
    ``DEDENT``, etc.)

    By default, ``COMMMENT`` tokens are not included in the count.
    If you wish to include them, set ``exclude_comment`` to ``False``.
    """
    warnings.warn(
        "get_number() will soon be removed. Replace by getting a list of significant tokens",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    nb = len(tokens)
    for token in tokens:
        if token.is_space():
            nb -= 1
        elif exclude_comment and token.is_comment():
            nb -= 1
    return nb


def dedent(tokens, nb):
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with the first nb characters removed.
    """
    # currently used in ideas
    # a bit dangerous as there is no check to see if the character removed
    # are not significant.
    line = untokenize(tokens)
    line = line[nb:]
    return tokenize(line)


# This can probably be eliminated; not used anywhere
def indent(tokens, nb, tab=False):
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with nb space characters inserted at the beginning.

    If ``tab`` is specified to be ``True``, ``nb`` tab characters are inserted
    instead of spaces.
    """
    warnings.warn(
        "indent() will soon be removed.",
        TokenUtilsDeprecationWarning,
        stacklevel=2
    )
    line = untokenize(tokens)
    if tab:
        line = "\t" * nb + line
    else:
        line = " " * nb + line
    return tokenize(line)


__all__ = ["__all__"]
_names = dir()


def _make_all():
    for name in _names:
        if not name.startswith("_"):
            __all__.append(name)


_make_all()
_make_all()
__all__.remove("__all__")
__all__.remove("TokenUtilsDeprecationWarning")
