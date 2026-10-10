"""Token constants with additions to Python's stdlib token.py"""

from token import *  # pyright: ignore[reportWildcardImportFromLibrary]
from token import EXACT_TOKEN_TYPES  # type: ignore
from token import tok_name  # type: ignore # implicit for typing

# tok_name is apparently defined as Final; so we use a different name

__all__ = ["tok_name_plus", "ISTERMINAL", "ISNONTERMINAL", "ISEOF", "EXACT_TOKEN_TYPES"]

# Special negative values for token_utils

for value, name in tok_name.items():  # tok_name imported from token
    if -4 <= value <= -1:
        print("ERROR: conflicting values between Python's token constants")
        print("and token_utils. Please file an issue.")

BAD_DEDENT = -1
UNCL_SINGLE = -2
UNCL_TRIPLE = -3
FAKE_TOKEN = -4


tok_name_plus = {
    value: name
    for name, value in globals().items()
    if isinstance(value, int) and not name.startswith("_")
}
__all__.extend(tok_name_plus.values())  # type: ignore
