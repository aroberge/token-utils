from ast import literal_eval as py_literal_eval
from keyword import iskeyword as py_iskeyword

from token_utils import py_tokenize

_token_format = "type={type}  string={string}  start={start}  end={end}  line={line}"


class Token:
    """Token as generated from Python's tokenize.generate_tokens written here in
    a more convenient form, and with some custom methods.

    The various parameters are::

        type: token type
        string: the token written as a string
        start = (start_row, start_col)
        end = (end_row, end_col)
        line: entire line of code where the token is found.

    Token instances are mutable objects. Therefore, given a list of tokens,
    we can change the value of any token's attribute, untokenize the list and
    automatically obtain a transformed source.
    """

    def __init__(self, token):
        """Initializes using a token produced by Python's tokenize function as input."""
        self.type = token[0]
        self.string = token[1]
        self.start = self.start_row, self.start_col = token[2]
        self.end = self.end_row, self.end_col = token[3]
        self.line = token[4]

    def __eq__(self, other):
        """Compares a Token with another object; returns true if
        self.string == other.string or if self.string == other.
        """
        if hasattr(other, "string"):
            return self.string == other.string
        elif isinstance(other, str):
            return self.string == other
        else:
            raise TypeError(
                "A token can only be compared to another token or to a string."
            )

    def __repr__(self):
        """Nicely formatted token to help with debugging session.

        Note that it does **not** print a string representation that could be
        used to create a new ``Token`` instance, which is something you should
        never need to do other than indirectly by using the functions
        provided in this module.
        """
        return _token_format.format(
            type="%s (%s)" % (self.type, py_tokenize.tok_name[self.type]),
            string=repr(self.string),
            start=str(self.start),
            end=str(self.end),
            line=repr(self.line),
        )

    def __str__(self):
        """Returns the string attribute."""
        return self.string

    def __contains__(self, str_arg):
        """Returns True if the string argument is a substring of the token string attribute"""
        if not isinstance(str_arg, str):
            return False
        return str_arg in self.string

    def __len__(self):
        """Returns the length of the string attribute"""
        return len(self.string)

    def is_comment(self):
        """Returns True if the token is a comment."""
        return self.type == py_tokenize.COMMENT

    def is_complex(self):
        """Returns True if the token represents a complex number.cavie"""
        return self.is_number() and isinstance(py_literal_eval(self.string), complex)

    def is_float(self):
        """Returns True if the token represents a float."""
        return self.is_number() and isinstance(py_literal_eval(self.string), float)

    def is_identifier(self):
        """Returns ``True`` if the token represents a valid Python identifier
        excluding Python keywords.

        Note: this is different from Python's string method ``isidentifier``
        which also returns ``True`` if the string is a keyword.
        """
        return self.string.isidentifier() and not self.is_keyword()

    def is_integer(self):
        """Returns True if the token represents an integer"""
        return self.is_number() and isinstance(py_literal_eval(self.string), int)

    def is_keyword(self):
        """Returns True if the token represents a Python keyword."""
        return py_iskeyword(self.string)

    def is_name(self):
        """Returns ``True`` if the token is a type NAME"""
        return self.type == py_tokenize.NAME

    def is_number(self):
        """Returns True if the token represents a number."""
        return self.type == py_tokenize.NUMBER

    def is_operator(self) -> bool:
        """Returns true if the token is of type OP"""
        return self.type == py_tokenize.OP

    def is_space(self):
        """Returns True if the token indicates a change in indentation,
        the end of a line, or the end of the source
        (``INDENT``, ``DEDENT``, ``BAD_DEDENT``, ``NEWLINE``,
        ``NL``, and ``ENDMARKER``).

        Note that spaces, including tab characters ``\\t``, between tokens
        on a given line are not considered to be tokens themselves.
        """
        return self.type in (
            py_tokenize.INDENT,
            py_tokenize.DEDENT,
            py_tokenize.BAD_DEDENT,
            py_tokenize.NEWLINE,
            py_tokenize.NL,
            py_tokenize.ENDMARKER,
        )

    def is_indentation(self):
        """Returns True if the token indicates a change in indentation,
        (``INDENT``, ``DEDENT``, ``BAD_DEDENT``).
        """
        return self.type in (
            py_tokenize.INDENT,
            py_tokenize.DEDENT,
            py_tokenize.BAD_DEDENT,
        )

    def is_string(self):
        """Returns True if the token represents a string"""
        return self.type == py_tokenize.STRING
