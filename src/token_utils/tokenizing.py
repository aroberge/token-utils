"""
tokenizing.py
==============

All the functions dealing with tokenizing/untokenizing.
"""

from io import StringIO
import warnings

from token_utils import _py_tokenize
from token_utils.token_class import Token
from token_utils.custom_warnings import SemiColonWarning
from token_utils.utils import pairwise


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
        for tok in _py_tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
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


def tokenize(source):
    """Transforms a source (string) into a list of Tokens."""

    return list(generate_tokens(source))


def get_physical_lines(source, remove_comments=True):
    """Transforms a source (string) into a list of of list of Tokens,
    with each (inner) list containing all the tokens found on a given
    physical line of code except comments that correspond to indentation.

    Note that lines visually separated by a continuation character (``\\``)
    are considered to be part of the same physical line

    Thus, for a given (inner) list of tokens, the first token (list[0])
    will either be:

    - A newline character (``NL`` or ``NEWLINE`` token)
    - A significant (non-space) token.
    - An ``ENDMARKER`` token

    Similarly, the last token (list[-1]) will be a either
    a new line character (``NL`` or ``NEWLINE`` token) or ``ENDMARKER`` token.

    Set ``remove_comments`` to ``False`` to keep comments.
    In that case, the first token oa an inner list could be a comment.

    ## If one needs lines with Indentation information still present,
    ## see Issue #14.
    """
    lines = []
    new_line = []
    for token in generate_tokens(source):
        if token.is_newline():
            new_line.append(token)
            lines.append(new_line)
            new_line = []
            continue
        elif token.is_indentation():
            continue
        if remove_comments and token.is_comment():
            continue
        new_line.append(token)
    if new_line:
        lines.append(new_line)
    return lines


def get_logical_lines(source, remove_comments=True, remove_semi_colons=True):
    """This retrieves logical lines, each essentially correponding to a single statement.

    Warning: untokenize(get_logical_lines) != source in general. However, the
    untokenized version executes the same as the original.

    When two or more physical lines are joined **explitly** into logical lines
    using backslash characters (`\\`) or **implicitly** by using
    parentheses, square brackets or curly braces opening on a given physical line
    and closing on another, the ``NL`` token is used to indicate that a ``\\n``
    was used. By removing these continuation symbol, or signs, we can potentially
    combine many physical line into a single logical line ~ statement.
    (Note that we could have multiple statements separated by semi-colons ``;``.)

    Empty lines (or lines with only comments) also end with an ``NL`` token.

    This function extract logical lines, removing all space tokens (``INDENT``, etc.)
    ``NL`` as well as ``ENDMARKER``. This makes it possible
    to focus on tokens that are relevant for modifying the syntax,
    with the exception of ``NEWLINE``.
    """
    lines = []
    new_line = []
    for token, next_ in pairwise(generate_tokens(source)):
        if token.type == _py_tokenize.NEWLINE:
            new_line.append(token)
            lines.append(new_line)
            new_line = []
            continue
        elif token.type == _py_tokenize.NL:
            continue
        elif token.is_indentation():
            continue
        elif token.is_comment() and remove_comments:
            continue
        elif token == ";" and next_.is_newline() and remove_semi_colons:
            continue
        elif token == ";" and token.start_row > 1 and remove_semi_colons:
            warnings.warn(
                f"Semi-colon found on line {token.start_row}",
                SemiColonWarning,
                stacklevel=2,
            )
        elif token.type == _py_tokenize.ENDMARKER:
            break
        new_line.append(token)

    if new_line:
        lines.append(new_line)
    return lines


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
    # 3. We accept lines of lines of tokens
    # Begin code (for extraction by Sphinx)
    # Allow both lists of Tokens or strings, or lists of lists of Tokens or strings
    if isinstance(tokens[0], list):
        tokens = [token for line in tokens for token in line]
    assert isinstance(tokens[0], (Token, str))

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
    inserting spaces instead. For example, removing "two"::

        |one two three|  -->
        |one     three|

    If no token has been removed from a tokenized list, and no
    tab characters are used for indentation or spacing between tokens,
    it should return the same content as untokenize.

    It allows for easy removal of comments with ``remove_comments=True``.
    As long as one does not care about tab characters, it is slightly more
    efficient to use::

        stringify(tokenize(source), remove_comments=True)

    than::

        ideas.utils.remove_comments(source)
    """
    if isinstance(tokens[0], list):
        tokens = [token for line in tokens for token in line]

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

        # Preserve escaped newlines.
        if (
            not remove_comments
            and last_non_whitespace_token_type != _py_tokenize.COMMENT
            and token.start_row > last_row
            and previous_line.endswith(("\\\n", "\\\r\n", "\\\r"))
        ):
            words.append(previous_line[len(previous_line.rstrip(" \t\n\r\\")) :])

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column and not token.is_space():
            # Insert spaces instead of the content that was skipped between tokens
            # except at the end of line before a NL or NEWLINE token
            words.append(" " * (token.start_col - last_column))

        words.append(token.string)

        previous_line = token.line
        last_row = token.end_row
        last_column = token.end_col
        if not token.is_space():
            last_non_whitespace_token_type = token.type

    return "".join(words)


def print_tokens(source):
    """Prints tokens found in source, line by line, followed by a
       string version of that line.

    ``source`` is either a string to be tokenized, a list of Token objects,
    or a list of lists of tokens.

    This can be useful as a debugging tool.
    """

    if isinstance(source[0], list):
        print("Printing list of lists of tokens:\n")
        for line in source:
            for token in line:
                print(repr(token))
            print("  --> line: ", repr(stringify(line)))
        return

    if isinstance(source[0], Token):
        print("Printing list of tokens:\n")
        line = []
        for token in source:
            print(repr(token))
            if token == "\n":
                line.append(token)
                print("  --> line: ", repr(stringify(line)))
                line = []
                continue
            line.append(token)

        if line:
            print("  --> line: ", repr(stringify(line)))
            return

    print("Printing physical lines from source (indent tokens removed):\n")
    for line in get_physical_lines(source):
        for token in line:
            print(repr(token))
        print("  --> line: ", repr(stringify(line)))


def dedent(tokens, nb):
    """Given a list of tokens representing a single physical line,
    produces an equivalent list corresponding
    to a line of code with the first nb characters removed.

    If the list doesn't include any tokens, or if a negative
    value for nb is given, a ``ValueError`` is raised.

    If an attempt to remove non-space characters is made,
    a ``TypeError`` is raised.
    """
    # The "indent" part is probably not needed...
    if len(tokens) == 0:
        raise ValueError("Empty list of tokens was passed to dedent()/indent().")
    if nb < 0:
        raise ValueError("'nb' must be a positive number in dedent().")

    line = untokenize(tokens)
    begin = line[:nb]
    end = line[nb:]
    if begin.strip():
        raise TypeError("Attempting to remove non-space character in dedent().")
    return tokenize(end)


__all__ = [
    "generate_tokens",
    "tokenize",
    "get_physical_lines",
    "get_logical_lines",
    "untokenize",
    "stringify",
    "print_tokens",
    "dedent",
]
