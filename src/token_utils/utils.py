"""
utils.py
------------------

A collection of various functions to find different tokens.
"""

from token_utils.tokenizing import get_significant_tokens, tokenize, untokenize


def find_substring_index(main, substring):
    """Somewhat similar to the find() method for strings,
    this function determines if the tokens for substring appear
    as a subsequence of the tokens for main. If so, the index
    of the first token in returned, otherwise -1 is returned.
    """
    # used once in friendly-traceback; not sure it is worth keeping!
    main_tokens = [
        tok.string for tok in get_significant_tokens(main) if tok.string.strip()
    ]
    sub_tokens = [
        tok.string for tok in get_significant_tokens(substring) if tok.string.strip()
    ]
    for index, token in enumerate(main_tokens):
        if (
            token == sub_tokens[0]
            and main_tokens[index : index + len(sub_tokens)] == sub_tokens
        ):
            return index
    return -1


# this can be eliminated by using significant tokens and [0]
# However, it is currently used in ideas, so we need to change the
# code there first.
def get_first(tokens, exclude_comment=True):
    """Given a list of tokens, find the first token which is not a space token
    (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) and,
    by default, also not a ``COMMMENT``.

    ``COMMMENT`` tokens can be included by setting ``exclude_comment`` to ``False``.

    Returns ``None`` if none is found.
    """
    for token in tokens:
        if token.is_space() or (exclude_comment and token.is_comment()):
            continue
        return token
    return None


# this can be eliminated by using significant tokens and [0]
# However, it is currently used in ideas, so we need to change the
# code there first.
def get_first_index(tokens, exclude_comment=True):
    """Given a list of tokens, find the index of the first token which is
    not a space token (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) nor
    a ``COMMMENT``. If it is desired to include COMMENT, set ``exclude_comment``
    to ``True``.

    Returns ``None`` if none is found.
    """
    for index, token in enumerate(tokens):
        if token.is_space() or (exclude_comment and token.is_comment()):
            continue
        return index
    return None


# this can be eliminated by using significant tokens and [-1]
# However, it is currently used in ideas, so we need to change the
# code there first.
def get_last(tokens, exclude_comment=True):
    """Given a list of tokens, find the last token which is not a space token
    (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) and, by default,
    also not a ``COMMMENT``.

    ``COMMMENT`` tokens can be included by setting``exclude_comment``
    to ``False``.

    Returns ``None`` if none is found.
    """
    return get_first(reversed(tokens), exclude_comment=exclude_comment)


# this can be eliminated by using significant tokens and [0]
# However, it is currently used in ideas, so we need to change the
# code there first.
def get_last_index(tokens, exclude_comment=True):
    """Given a list of tokens, find the index of the last token which is
    not a space token (such as a ``NEWLINE``, ``INDENT``, ``DEDENT``, etc.) nor
    a ``COMMMENT``. If it is desired to include COMMENT, set ``exclude_comment``
    to True.

    Returns ``None`` if none is found.
    """
    return (
        len(tokens)
        - 1
        - get_first_index(reversed(tokens), exclude_comment=exclude_comment)
    )


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
        if not name.startswith("_") and not name.startswith("py"):
            __all__.append(name)


_make_all()
