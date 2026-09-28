# decimal_tok.py

from token_utils import tokenize, untokenize


def float_to_decimal(source):
    tokens = tokenize(source)
    for token in tokens:
        if token.is_float():
            token.string = f"Decimal('{token.string}')"
    return untokenize(tokens)
