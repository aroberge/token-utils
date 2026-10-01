import sys
import warnings


class TokenUtilsEOFWarning(UserWarning):
    """Raised when and EOF condition is reached."""

    pass


def disable_warnings():
    """Disable all warnings arising from token_utils."""

    warnings.filterwarnings("ignore", category=TokenUtilsEOFWarning)


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    """Simply show the category and message, as the rest of the potential output
    would not be useful.
    """
    output_file = file if file is not None else sys.stderr
    # Format your warning message cleanly without extra newlines
    msg = f"\n {category.__name__}: {message}\n"
    output_file.write(msg)


warnings.showwarning = custom_showwarning
