from typing import TextIO

class TokenUtilsEOFWarning(UserWarning): ...
class SemiColonWarning(UserWarning): ...

def disable_warnings() -> None: ...
def custom_showwarning(
    message: str,
    category: Warning,
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
) -> None: ...
