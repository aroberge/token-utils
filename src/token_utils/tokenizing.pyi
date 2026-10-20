from token_utils.token_class import Token
from collections.abc import Iterator, MutableSequence

def _fix_empty_line(
    source: str, prev_token: Token | None, last_token: Token
) -> Token: ...
def generate_tokens(source: str) -> Iterator[Token]: ...
def tokenize(source: str) -> MutableSequence[Token]: ...
def get_physical_lines(
    source: str, remove_comments: bool = True
) -> Iterator[MutableSequence[Token]]: ...
def get_logical_lines(
    source: str, remove_comments: bool = True, remove_semi_colons: bool = True
) -> Iterator[MutableSequence[Token]]: ...
def untokenize(
    tokens: (
        MutableSequence[Token | str] | MutableSequence[MutableSequence[Token | str]]
    ),
) -> str: ...
def stringify(
    tokens: (
        MutableSequence[Token | str] | MutableSequence[MutableSequence[Token | str]]
    ),
    remove_comments: bool = False,
) -> str: ...
def print_tokens(
    tokens: str | MutableSequence[Token] | MutableSequence[MutableSequence[Token]],
) -> None: ...
def dedent(tokens: MutableSequence[Token], nb: int) -> MutableSequence[Token]: ...

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
