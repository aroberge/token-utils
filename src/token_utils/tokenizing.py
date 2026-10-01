"""
tokenizing.py
==============

All the functions dealing with tokenizing/untokenizing.
"""

from token_utils import _py_tokenize

from io import StringIO as _StringIO

from token_utils.token_class import Token as _Token


def _fix_empty_line(source, prev_token, last_token):
    """Our tokenizer is based on Python's 3.11 tokenizer
    which drops entirely a last line if it consists only of
    space characters and/or tab characters.

    To ensure that we can always have::

        untokenize(tokenize(source)) == source

    we correct the last token content if needed.
    """
    if prev_token is None:
        print("WARNING: _fix_empty_line was called with prev_token==None.")
        print("This should never happen. Please file an issue and include")
        print("the source that produced this result.")
        return last_token

    if prev_token.line.endswith((" ", "\t")):  # fix not needed
        return last_token

    new_chars = []
    for char in reversed(source):
        if char in (" ", "\t"):
            new_chars.insert(0, char)
        else:
            break
    last_token.string = "".join(new_chars)
    return last_token


def generate_tokens(source):
    """Tokenize a source (string) yielding tokens one at a time."""
    # Unfortunately, there is still a bug in py_tokenize._tokenize
    # that drops entirely a last line
    # if it consists only of space characters and/or tab characters.
    # So, we keep watch for the last token (ENDMARKER) and
    # apply a fix if needed.
    prev_token = None
    perhaps_fix_needed = source.endswith((" ", "\t"))
    try:
        for tok in _py_tokenize.generate_tokens(_StringIO(source).readline):
            token = _Token(tok)
            if token.type != _py_tokenize.ENDMARKER or not perhaps_fix_needed:
                yield token
            else:
                if not source.strip():  # We were passed a useless string!
                    token.string = source
                    yield token
                else:
                    yield _fix_empty_line(source, prev_token, token)
            prev_token = token
    except Exception as exc:
        print(
            "WARNING: the following unexpected error was raised in ",
            "token_utils' generate_tokens().\n",
            "Please report this as an issue, including the source that produced this.",
        )
        print(exc, repr(exc))


def tokenize(source, warning=True):
    """Transforms a source (string) into a list of Tokens."""

    return list(generate_tokens(source))


def get_significant_tokens(source):
    """Gets a list of tokens from a source (str), removing
    any token that signal a change in indentation.
    """
    # This is useful when we want to analyze the content of a
    # line and want to identify a first 'significant' token
    # as it will be the first of the line!
    tokens = []
    for token in generate_tokens(source):
        if token.is_indentation():
            continue
        tokens.append(token)

    return tokens


def get_lines(source):
    """Transforms a source (string) into a list of of list of Tokens,
    with each (inner) list containing all the tokens found on a given
    line of code.
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


def get_stripped_lines(source):
    """Transforms a source (string) into a list of of list of Tokens,
    with each (inner) list containing all the tokens found on a given
    line of code except that any token related to change in
    indentation and comments will have been removed. Thus, for a given
    (inner) list of tokens, list[0] will be a non-space token.
    """
    lines = []
    current_row = -1
    new_line = []
    first_token = ""
    for token in generate_tokens(source):
        if token.start_row != current_row:
            current_row = token.start_row
            if new_line:
                lines.append(new_line)
            elif first_token:
                lines.append([first_token])
            new_line = []
            first_token = token
        if not (token.is_indentation() or token.is_comment()):
            new_line.append(token)
    if new_line:
        lines.append(new_line)
    return lines


def untokenize_lines_of_tokens(lines):
    """Given a line of lines of tokens, such as that
    obtained by ``get_lines()`` or ``get_stripped_lines``,
    returns a string containing the source.

    The following should be true::

        untokenize_lines_of_tokens(get_lines(source)) == source
    """
    tokens = [token for line in lines for token in line]
    return untokenize(tokens)


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

    It is often more effective to "mutate" a token string to insert new
    content.

    Finally, while token_utils only deals with sources as string,
    and doesn't do encoding, this function will drop tokens
    identified as being of type ``ENCODING``, which would mean that they
    came from another source.
    """
    # Main changes from original:
    # 1. We accumulate substrings in a list, rather than concatenating them
    #    as we go along
    # 2. We allow the inclusion of pure strings as token, but without
    #    taking their length into consideration.
    # Begin code (for extraction by Sphinx)
    words = []
    previous_line = ""
    last_row = 0
    last_column = -1
    last_non_whitespace_token_type = None

    for token in tokens:
        if isinstance(token, str):
            words.append(token)
            continue
        if token.type == _py_tokenize.ENCODING:
            continue

        # Preserve escaped newlines.
        if (
            last_non_whitespace_token_type != _py_tokenize.COMMENT
            and token.start_row > last_row
            and previous_line.endswith(("\\\n", "\\\r\n", "\\\r"))
        ):
            words.append(previous_line[len(previous_line.rstrip(" \t\n\r\\")) :])

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column:
            # Insert the content that was skipped between tokens
            words.append(token.line[last_column : token.start_col])

        words.append(token.string)

        previous_line = token.line
        last_row = token.end_row
        last_column = token.end_col
        if not token.is_space():
            last_non_whitespace_token_type = token.type

    return "".join(words)
    # End code (for extraction by Sphinx)


def stringify(tokens, remove_comments=False):
    """Returns a string built from tokens.

    It is somewhat similar to untokenize except that it doesn't add any
    missing information from tokens that might have been removed,
    nor does it care about continuation characters.

    If not token has been removed from a tokenized list, and no
    continuation character is present, and no tab characters are used for
    indentation, it should return the same content as untokenize.
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
        if token.type == _py_tokenize.ENCODING:
            continue
        if remove_comments and token.is_comment():
            continue

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column:
            # Insert spaces instead of the content that was skipped between tokens
            words.append(" " * (token.start_col - last_column))

        words.append(token.string)
        last_row = token.end_row
        last_column = token.end_col

    return "".join(words)


def print_tokens(source):
    """Prints tokens found in source, excluding spaces and comments.

    ``source`` is either a string to be tokenized, or a list of Token objects.

    This is occasionally useful as a debugging tool.
    """
    if isinstance(source[0], _Token):
        source = untokenize(source)

    for lines in get_lines(source):
        for token in lines:
            print(repr(token))
        print()


__all__ = ["__all__"]
_names = dir()


def _make_all():
    for name in _names:
        if not name.startswith("_"):
            __all__.append(name)


_make_all()
__all__.remove("__all__")
