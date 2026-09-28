from token_utils.token_class import Token, make_fake_token  # noqa
from token_utils.tokenizing import *
from token_utils.utils import *
from token_utils.__about__ import version  # noqa


def disable_warnings():
    """Disable all warnings arising from token_utils."""
    import warnings
    from token_utils.utils import TokenUtilsDeprecationWarning
    from token_utils.py_tokenize import TokenUtilsEOFWarning

    warnings.filterwarnings("ignore", category=TokenUtilsDeprecationWarning)
    warnings.filterwarnings("ignore", category=TokenUtilsEOFWarning)
