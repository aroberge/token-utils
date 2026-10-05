# factorial_2.py

from token_utils import (
    tokenize,
    untokenize,
    add_operator,
    pairwise,
    BracketStack,
    split_at_token,
)

add_operator("!", "exclamation")


def make_factorial(source):
    tokens = tokenize(source)
    stack = BracketStack()
    new_tokens = []

    for token, next_ in pairwise(tokens):
        if (
            next_ == "!"
            and token.is_immediately_before(next_)
            and (token.is_integer() or token.is_identifier())
        ):
            token.string = f"factorial({token.string})"
            next_.string = ""
        elif next_ == "!" and token.is_immediately_before(next_) and token == ")":
            matching_bracket = stack.add(token)
            next_.string = ""
            new_tokens, remainder = split_at_token(new_tokens, matching_bracket)
            matching_bracket.string = "factorial("
            new_tokens.append(matching_bracket)
            new_tokens.extend(remainder)
        else:
            if token.is_bracket():
                stack.add(token)
        new_tokens.append(token)

    return untokenize(new_tokens)
