from _typeshed import Incomplete

import sys
import warnings

class TokenUtilsEOFWarning(UserWarning): ...
class SemiColonWarning(UserWarning): ...

def disable_warnings() -> None: ...
def custom_showwarning(
    message: str,
    category: Warning,
    filename: str,
    lineno: int,
    file: Incomplete = None,
    line: Incomplete = None,
) -> None: ...
