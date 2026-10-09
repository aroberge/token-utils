from typing import Literal

from token import *
from token import EXACT_TOKEN_TYPES

__all__ = ["tok_name", "ISTERMINAL", "ISNONTERMINAL", "ISEOF", "EXACT_TOKEN_TYPES"]
BAD_DEDENT: Literal[-1]
UNCL_SINGLE: Literal[-2]
UNCL_TRIPLE: Literal[-3]
FAKE_TOKEN: Literal[-4]
tok_name: dict[int, str]
