"""token_utils.utils.py
------------------

A collection of useful functions and methods to deal with tokenizing
source code.
"""

from token_utils import py_tokenize

from io import StringIO as _StringIO

from token_utils.token_class import Token


def fix_empty_line(source, prev_token, last_token):
    """Our tokenizer is based on Python's 3.11 tokenizer
    which drops entirely a last line if it consists only of
    space characters and/or tab characters.

    To ensure that we can always have::

        untokenize(tokenize(source)) == source

    we correct the last token content if needed.
    """
    print(f"{last_token=}")
    if prev_token is None:  # should not happen
        return last_token
    if prev_token.line.endswith((" ", "\t")):  # fix not needed
        return last_token

    nb = 0
    for char in reversed(source):
        if char in (" ", "\t"):
            nb += 1
        else:
            break
    last_token.string = source[-nb:]
    assert nb > 0
    print(f"Fix applied {last_token=}")
    return last_token


def generate_tokens(source):
    """Tokenize a source (string) yielding tokens one at a time."""
    # Unfortunately, there is still a bug in py_tokenize._tokenize
    # that drops entirely a last line
    # if it consists only of space characters and/or tab characters.
    # So, we keep watch for the last token (ENDMARKER) and
    # apply a fix if needed.
    prev_token = None
    fix_needed = source.endswith((" ", "\t"))
    try:
        for tok in py_tokenize.generate_tokens(_StringIO(source).readline):
            token = Token(tok)
            if token.type != py_tokenize.ENDMARKER or not fix_needed:
                yield token
            else:
                yield fix_empty_line(source, prev_token, token)
            prev_token = token
    except Exception as exc:
        print(
            "WARNING: the following unexpected error was raised in ",
            f"{__name__}.generate_tokens\n",
            "Please report this as an issue.",
        )
        print(exc, repr(exc))


def tokenize(source, warning=True):
    """Transforms a source (string) into a list of Tokens."""

    return list(generate_tokens(source))


def get_significant_tokens(source):
    """Gets a list of tokens from a source (str), ignoring comments
    as well as any token whose string value is either null or
    consists of spaces, newline or tab characters.
    """
    tokens = []
    for token in generate_tokens(source):
        if not token.string.strip():
            continue
        if token.is_comment():
            continue
        tokens.append(token)

    return tokens


def get_lines(source):
    """Transforms a source (string) into a list of Tokens, with each
    (inner) list containing all the tokens found on a given line of code.
    """
    lines = []
    current_row = -1
    new_line = []
    for token in generate_tokens(source):
        if token.start_row != current_row:
            current_row = token.start_row
            if new_line:
                lines.append(new_line)
            new_line = []
        new_line.append(token)
    if new_line:
        lines.append(new_line)
    return lines


# this can be eliminated by using significant tokens and len()
# However, it is currently used in ideas, so we need to change the
# code there first.
def get_number(tokens, exclude_comment=True):
    """Given a list of tokens, gives a count of the number of
    tokens which are not space tokens (such as ``NEWLINE``, ``INDENT``,
    ``DEDENT``, etc.)

    By default, ``COMMMENT`` tokens are not included in the count.
    If you wish to include them, set ``exclude_comment`` to ``False``.
    """
    nb = len(tokens)
    for token in tokens:
        if token.is_space():
            nb -= 1
        elif exclude_comment and token.is_comment():
            nb -= 1
    return nb


def strip_comment(line):
    """Removes comments from a line"""
    tokens = []
    try:
        for tok in py_tokenize.generate_tokens(_StringIO(line).readline):
            token = Token(tok)
            if token.is_comment():
                continue
            tokens.append(token)
    except py_tokenize.TokenError:
        pass
    return untokenize(tokens)


# TODO: add unit test for this
def find_substring_index(main, substring):
    """Somewhat similar to the find() method for strings,
    this function determines if the tokens for substring appear
    as a subsequence of the tokens for main. If so, the index
    of the first token in returned, otherwise -1 is returned.
    """
    main_tokens = [tok.string for tok in get_significant_tokens(main)]
    sub_tokens = [tok.string for tok in get_significant_tokens(substring)]
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


def untokenize(tokens):
    """Return source code based on tokens.

    Adapted from https://github.com/myint/untokenize,
    Copyright (C) 2013-2018 Steven Myint, MIT License (same as this project).

    This is similar to Python's own tokenize.untokenize(), except that it
    preserves spacing between tokens, by using the line
    information recorded by Python's tokenize.generate_tokens.
    As a result, if the original soure code had multiple spaces between
    some tokens or if escaped newlines were used or if tab characters
    were present in the original source, those will also be present
    in the source code produced by untokenize.

    Thus ``source == untokenize(tokenize(source))``.

    Note: if you you modifying tokens from an original source:

    Instead of full token object, ``untokenize`` will accept simple
    strings; however, it will only insert them *as is* without taking them
    into account when it comes with figuring out spacing between tokens.
    """
    words = []
    previous_line = ""
    last_row = 0
    last_column = -1
    last_non_whitespace_token_type = None

    for token in tokens:
        if isinstance(token, str):
            words.append(token)
            continue
        if token.type == py_tokenize.ENCODING:
            continue

        # Preserve escaped newlines.
        if (
            last_non_whitespace_token_type != py_tokenize.COMMENT
            and token.start_row > last_row
        ):
            if previous_line.endswith(("\\\n", "\\\r\n", "\\\r")):
                words.append(previous_line[len(previous_line.rstrip(" \t\n\r\\")) :])

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column:
            words.append(token.line[last_column : token.start_col])

        words.append(token.string)

        previous_line = token.line
        last_row = token.end_row
        last_column = token.end_col
        if not token.is_space():
            last_non_whitespace_token_type = token.type

    return "".join(words)


def print_tokens(source):
    """Prints tokens found in source, excluding spaces and comments.

    ``source`` is either a string to be tokenized, or a list of Token objects.

    This is occasionally useful as a debugging tool.
    """
    if isinstance(source[0], Token):
        source = untokenize(source)

    for lines in get_lines(source):
        for token in lines:
            print(repr(token))
        print()


__all__ = ["__all__"]
_names = dir()


def _make_all():
    for name in _names:
        if not name.startswith("_") and not name.startswith("py"):
            __all__.append(name)


_make_all()
