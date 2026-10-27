from token_utils.token_class import Token, make_fake_token, add_operator, NULL
from token_utils.tokenizing import (
    generate_tokens,
    tokenize,
    get_logical_lines,
    get_physical_lines,
    get_significant_tokens,
    untokenize,
    stringify,
    dedent,
    print_tokens,
)

from token_utils.utils import (
    BracketStack,
    IndentStack,
    pairwise,
    sliding_window,
    split_at_token,
    OrphanedClosingBracket,
    MismatchedBrackets,
)  # noqa
from token_utils.__about__ import version
from token_utils.custom_warnings import disable_warnings


def is_invisible_control_character(char):
    """Used to determine if a character would be visible when printed."""
    if len(char) != 1:  # protect against invalid input
        return False
    n = ord(char)
    if 0 <= n <= 0x1F or n == 0x7F or 0x80 <= n <= 0x9F:
        return char
    return False


__all__ = [
    "Token",
    "NULL",
    "make_fake_token",
    "add_operator",
    "BracketStack",
    "IndentStack",
    "pairwise",
    "sliding_window",
    "split_at_token",
    "version",
    "disable_warnings",
    "generate_tokens",
    "tokenize",
    "get_physical_lines",
    "get_logical_lines",
    "untokenize",
    "stringify",
    "print_tokens",
    "dedent",
    "is_invisible_control_character",
]
