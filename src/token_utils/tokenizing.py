"""
tokenizing.py
==============

All the functions dealing with tokenizing/untokenizing.
"""

from collections import deque
from itertools import chain, islice
from io import StringIO
import warnings

from token_utils import _py_tokenize
from token_utils.token_class import Token, make_fake_token
from token_utils.custom_warnings import SemiColonWarning


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


def pairwise(iterable, prev=0):
    """Similar to itertools.pairwise (Python 3.10+). However, it adds a fake
    token at the end if ``prev==0`` (the default) or at the beginning
    if ``prev==1``. Any other value will result in a ``ValueError``

    Given a list of tokens represented by lower case letters, and a fake token by $,
    the default corresponds to something like::

        pairwise('abcde') → ab bc cd de e$
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
    and $ representing a fake token, we would have something like:

    sliding_window('abcde', 3) → abc bcd cde deF e$$

    With ``prev==1``, we would have 1 fake token prepended and
    one appended; thus

    sliding_window('abcde', 3, prev=1) → $ab abc bcd cde de$

    We must have ``0 <= prev <= n-1``, otherwise a ValueError is raised

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

    for token in generate_tokens(source):
        if token.is_comment():
            token.string = ""  # does not remove any space preceeding it.
        tokens.append(token)

    mid_removal = untokenize(tokens)
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
    line = untokenize(tokens)
    if nb >= 0:
        begin = line[:nb]
        end = line[nb:]
        if begin.strip():
            raise TypeError("Attempting to remove non-space character in dedent().")
        return tokenize(end)

    nb = -nb
    if len(line) == 0:
        return tokenize(" " * nb)
    first_char = line[0]
    if first_char == "\t":
        line = "\t" * nb + line
    else:
        line = " " * nb + line
    return tokenize(line)


def indent(tokens, n):
    """Calls dedent(tokens, -n) and adds the required number of spaces
    or tab characters as needed"""
    return dedent(tokens, -n)


class BracketStack:
    """Helpful in keeping track of open and close brackets in a token sequence.

    It is intended to be strict, and only accept Token instances, with open brackets
    added before any close one can be added.
    """

    def __init__(self):
        self.stack = []

    def add(self, bracket):
        """Adds a bracket to a stack.

        If it is a closing bracket that matches the last added one,
        that last opening one is returned.

        If it is a close bracket not matching the last added one, or the
        first one added, a TypeError is raised.

        If an open bracket is added, False is returned.
        """
        if not isinstance(bracket, Token):
            raise TypeError("'bracket' parameter must be a Token.")
        if self.stack:
            if bracket.is_matching_bracket(self.stack[-1]):
                return self.stack.pop()
            elif not bracket.is_open_bracket():
                raise TypeError(
                    f"Close bracket does not match anything: {repr(bracket)}"
                )
            else:
                self.stack.append(bracket)
                return False

        elif not bracket.is_open_bracket():
            raise TypeError(
                f"First bracket added cannot be a closing one: {repr(bracket)}"
            )
        else:
            self.stack.append(bracket)
            return False

    def is_empty(self):
        """Return True if the stack is empty, False if it contains brackets."""
        return not bool(self.stack)


class IndentStack:
    """docstring"""

    # In Python, the following keywords, or soft keywords, can signal the introduction
    # of an indented block::

    #     class, def, if/elif/else, for/else, try/except/else/finally, while/else, with, match, case

    # For some code analysis or code modification, it might be very useful of keeping track
    # of such keywords when they introduce a change in indentation. When they do so, and ignoring
    # end of line comments, they will appear as the first non-space token
    # on a **logical line** terminated by a colon ``:``.
    # If we use token-utils' ``get_logical_lines()`` to analyze some source code, the last token
    # of each such line will always be a ``NEWLINE`` token, preceded by a colon.
    # This allowed us to define the utility class ``IndentStack``.
    def __init__(self):
        self.stack = []
        self.top_indent_keywords = [
            "class",
            "def",
            "if",
            "for",
            "try",
            "while",
            "with",
            "match",
            "case",
        ]
        self.same_indent_keywords = [
            "elif",
            "else",
            "except",
            "finally",
        ]
        self.indent_keywords = self.top_indent_keywords + self.same_indent_keywords

    def print_stack(self):
        """Useful for diagnostic"""
        print([(tok.string, tok.start) for tok in self.stack])

    def top_item(self):
        """Returns the token at the top of the stack or None."""
        if not self.stack:
            return None
        return self.stack[-1]

    def update_indent(self, line):
        """Receives a line containing tokens. This line argument
        can be any **logical** line obtained using get_logical_lines().

        If the line signals a change in indentation, this function returns
        the last "top token" starting a line at that indentation. By "top token"
        we mean a token that can start a block such as ``if`` (for ``if/elif/else``),
        ``try``, etc.

        It returns None if there is no such token.
        """
        if not isinstance(line, list) or not line:
            raise TypeError("'line' parameter must be a list containing tokens")
        if not isinstance(line[0], Token):
            raise TypeError("'line' parameter must be a list containing tokens")
        # A relevant line will include at least a keyword, a colon and a NEWLINE token
        indenting_line = True
        first_token = line[0]

        if len(line) < 3:
            indenting_line = False
        elif not first_token.is_in(self.indent_keywords):
            indenting_line = False
        else:  # line could start with a soft keyword
            colon = line[-2]
            if colon != ":":
                indenting_line = False

        if not indenting_line:
            while self.stack:
                top_item = self.stack.pop()
                if top_item.start_col >= first_token.start_col:
                    continue
                self.stack.append(top_item)
                return top_item
            return None

        if not self.stack:
            self.stack.append(first_token)
            return first_token

        while True:
            top_item = self.stack.pop()

            # Indent: add popped item back and add new
            if top_item.start_col < first_token.start_col:
                self.stack.append(top_item)  # add back
                self.stack.append(first_token)
                return first_token

            # No change: depends if token starts new block or not
            if top_item.start_col == first_token.start_col:
                if first_token.is_in(self.top_indent_keywords):
                    # previous item at same level
                    self.stack.append(first_token)
                    return first_token
                else:
                    self.stack.append(top_item)
                    return top_item

            # Dedent; need to pop new item if possible
            if top_item.start_col > first_token.start_col:
                if not self.stack:
                    self.stack.append(first_token)
                    return first_token  # new item at top
                continue

    def is_inside_class(self):
        """Returns True if there is a line defining a class
        in the indentation stack."""
        for token in self.stack:
            if token == "class":
                return True
        return False

    def is_inside_def(self):
        """Returns True if there is a line defining a function
        in the indentation stack."""
        for token in self.stack:
            if token == "def":
                return True
        return False


def split_at_token(seq, token):
    """Split a list of tokens in two sublists: those occuring before the
    token specified, and those after."""
    before = []
    for index, tok in enumerate(seq):
        if tok.is_identical(token):
            break
        before.append(tok)
    after = seq[index + 1 :]
    return before, after


__all__ = ["__all__"]
_names = dir()


def _make_all():
    for name in _names:
        if not name.startswith("_"):
            __all__.append(name)


_make_all()
__all__.remove("__all__")
__all__.remove("Token")
__all__.remove("StringIO")
__all__.remove("chain")
__all__.remove("islice")
__all__.remove("deque")
