# decimal_tok2.py

from token_utils import generate_tokens, untokenize


def float_to_decimal(source):
    new_tokens = ["from decimal import Decimal\n\n"]
    for token in generate_tokens(source):
        if token.is_float():
            token.string = f"Decimal('{token.string}')"
        elif token.is_complex():
            token.string = "0.0"
        new_tokens.append(token)
    return untokenize(new_tokens)
