from token_utils.token_class import Token
from collections.abc import Iterator
from typing import List

def _fix_empty_line(
    source: str, prev_token: Token | None, last_token: Token
) -> Token: ...
def generate_tokens(
    source: str, keep_indent_tokens: bool = True, remove_comment: bool = False
) -> Iterator[Token]: ...
def tokenize(
    source: str, keep_indent_token: bool = True, remove_comments: bool = False
) -> List[Token]: ...
def get_physical_lines(
    source: str, keep_indent_tokens: bool = False, remove_comments: bool = True
) -> Iterator[list[Token]]: ...
def get_logical_lines(
    source: str,
    keep_indent_tokens: bool = False,
    remove_comments: bool = True,
    remove_semi_colons: bool = True,
) -> list[Token]: ...
def get_significant_tokens(source: str) -> list[Token]: ...
def untokenize(
    tokens: list[Token | str] | list[list[Token | str]],
) -> str: ...
def stringify(
    tokens: list[Token | str] | list[list[Token | str]],
    remove_comments: bool = False,
) -> str: ...
def print_tokens(
    tokens: str | list[Token] | list[list[Token]],
) -> None: ...
def dedent(tokens: list[Token], nb: int) -> list[Token]: ...

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
