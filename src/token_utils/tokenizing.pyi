from token_utils.token_class import Token
from collections.abc import Iterator
from typing import Sequence

def _fix_empty_line(
    source: str, prev_token: Token | None, last_token: Token
) -> Token: ...
def generate_tokens(source: str) -> Iterator[Token]: ...
def tokenize(source: str) -> Sequence[Token]: ...
def get_physical_lines(
    source: str, remove_comments: bool = True
) -> Iterator[Sequence[Token]]: ...
def get_logical_lines(
    source: str, remove_comments: bool = True, remove_semi_colons: bool = True
) -> Iterator[Sequence[Token]]: ...
def untokenize(
    tokens: Sequence[Token | str] | Sequence[Sequence[Token | str]],
) -> str: ...
def stringify(
    tokens: Sequence[Token | str] | Sequence[Sequence[Token | str]],
    remove_comments: bool = False,
) -> str: ...
def print_tokens(tokens: str | Sequence[Token] | Sequence[Sequence[Token]]) -> None: ...
def dedent(tokens: Sequence[Token], nb: int) -> Sequence[Token]: ...

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
