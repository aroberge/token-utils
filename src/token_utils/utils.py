from collections import deque
from itertools import chain, islice

from token_utils.token_class import Token, make_fake_token


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

    def add_top_indent_keyword(self, name):
        """Add a new top indent keyword, similar to class, def, try, etc.

        Useful when working with alternatives to standard Python syntax.
        """
        self.top_indent_keywords.append(name)
        self.indent_keywords = self.top_indent_keywords + self.same_indent_keywords

    def add_same_indent_keyword(self, name):
        """Add a new same indent keyword, similar to elif, else, except, etc.

        Useful when working with alternatives to standard Python syntax.
        """
        self.same_indent_keywords.append(name)
        self.indent_keywords = self.top_indent_keywords + self.same_indent_keywords

    def print_stack(self):
        """Useful for diagnostic"""
        print([(tok.string, tok.start) for tok in self.stack])

    def top_item(self):
        """Returns the token at the top of the stack or None."""
        if not self.stack:
            return None
        return self.stack[-1]

    def update(self, line):
        """Receives a line as a list containing tokens
        and keeps track of the indentation of the code.

        A line will deem to signal the beginning of an indented block if it begins
        with an appropriate keyword (``class, def, if, else, ...``) **and**
        ends with a colon. For this reason, it is highly recommended
        to obtain lines using ``get_logical_lines()`` since lines
        obtained using ``get_physical_lines()`` may have their last token
        on a different physical line.

        If the line signals a change in indentation (indent or dedent), this function returns
        the last "top token" starting a line at that indentation. By "top token"
        we mean a token that can start a block such as ``if`` (for ``if/elif/else``),
        ``try``, etc.

        It returns ``None`` if there is no such token.
        """
        if not (isinstance(line, list) or isinstance(line[0], Token)):
            raise TypeError(
                "'line' parameter must be a list containing 0 or more tokens"
            )
        for token in line:
            if not isinstance(token, Token):
                raise TypeError("'line' parameter must be a list only Token instances")

        first_token = line[0]
        if not first_token.string.strip():
            return None
        if first_token.is_comment():
            return None

        # An indenting line will include at least a relevant keyword,
        # a colon and a NEWLINE token
        indenting_line = True
        if len(line) < 3:
            indenting_line = False
        elif not first_token.is_in(self.indent_keywords):
            indenting_line = False
        else:  # line could start with a soft keyword
            colon = line[-2]
            if colon.is_comment():
                colon = line[-3]
            if colon != ":":
                indenting_line = False
        # What about if we have a one-liner like:
        #    def double(n): return n
        # While the colon will not have been found, such a line will NOT be the
        # beginning of an indented block. So, we only care to see if it signal
        # that we are leaving an indented block and dedenting the code

        if not indenting_line:  # is dedenting occuring?
            popped = 0
            while self.stack:
                top_item = self.stack.pop()
                popped += 1
                if top_item.start_col >= first_token.start_col:
                    continue

                if (top_item.start_col == first_token.start_col) and first_token.is_in(
                    self.top_indent_keywords
                ):  # new block at same level
                    self.stack.append(first_token)
                    return first_token

                self.stack.append(top_item)
                if popped > 1:
                    return top_item
                else:
                    return None
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

    def is_token_in_named_block(self, token, name):
        """Returns True if the token is indented more than
        a token with the name given.

        Example usage: figuring out if a 'def' represents
        a method of a class, or a pure function definition.
        """
        for tok in self.stack:
            if tok == name and tok.start_col < token.start_col:
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
