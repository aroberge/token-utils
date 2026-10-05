# factorial_1.py

from token_utils import tokenize, untokenize, add_operator, pairwise

add_operator("!", "exclamation")


def make_factorial(source):
    tokens = tokenize(source)
    new_tokens = []

    for token, next_ in pairwise(tokens):
        if (
            next_ == "!"
            and token.is_immediately_before(next_)
            and (token.is_integer() or token.is_identifier())
        ):
            token.string = f"factorial({token.string})"
            next_.string = ""
        new_tokens.append(token)

    return untokenize(new_tokens)
