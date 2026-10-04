import sys
import warnings


class TokenUtilsEOFWarning(UserWarning):
    """Raised when and EOF condition is reached."""

    pass


class SemiColonWarning(UserWarning):
    """Raised when a semi-colon is found separating statements
    on a logical line other than the first one.
    """

    # We don't warn if it's on the first line in case it's a
    # "one-liner" passed as an argument on a command line
    pass


def disable_warnings():
    """Disable all warnings arising from token_utils."""

    warnings.filterwarnings("ignore", category=TokenUtilsEOFWarning)
    warnings.filterwarnings("ignore", category=SemiColonWarning)


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    """Simply show the category and message, as the rest of the potential output
    would not be useful.
    """
    output_file = file if file is not None else sys.stderr
    # Format your warning message cleanly without extra newlines
    msg = f"\n {category.__name__}: {message}\n"
    output_file.write(msg)


warnings.showwarning = custom_showwarning
