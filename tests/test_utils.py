from token_utils import (
    generate_tokens,
    tokenize,
    make_fake_token,
    get_lines,
    dedent,
    pairwise,
    sliding_window,
    untokenize,
    strip_comments,
    BracketStack,
    stringify,  # for testing commment removal
)

source1 = "a = b"
source2 = "a = b # comment\n"
source3 = """
if True:
    a = b # comment
"""
tokens1 = tokenize(source1)
tokens2 = tokenize(source2)
lines2 = get_lines(source2)
lines3 = get_lines(source3)


def test_pairwise():
    # test with lists
    tokens = [make_fake_token(string=str(i)) for i in range(5)]
    new_tokens = []
    for _, token in pairwise(tokens, prev=1):
        new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]

    new_tokens = []
    for token, _ in pairwise(tokens):  # noqa
        new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]

    # test with generator
    new_tokens = []
    for _, token in pairwise(generate_tokens("0 1 2 3 4"), prev=1):
        if token.is_integer():
            new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]


def test_sliding_window():
    # tests with list
    tokens = [make_fake_token(string=str(i)) for i in range(5)]

    new_tokens = []
    for token, _, _ in sliding_window(tokens, 3):
        new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]

    new_tokens = []
    for _, token, _ in sliding_window(tokens, 3, prev=1):
        new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]

    new_tokens = []
    for _, _, token in sliding_window(tokens, 3, prev=2):
        new_tokens.append(str(token))
    assert new_tokens == ["0", "1", "2", "3", "4"]


def test_dedent():
    new_tokens = dedent(lines3[2], 4)
    assert new_tokens == tokens2


def test_indent():
    new_tokens = dedent(lines2[0], -4)
    new_line_a = untokenize(new_tokens)
    new_line_b = untokenize(lines3[2])
    assert new_line_a == new_line_b


# spaces between the last token and the comment
# would be left behind, so we put the comments
# right next to a non-space token for testing
with_comments = """
def test():  # a good function
    a = b  # fantastic mathematical operation
    return 3

# another comment to end things
"""

without_comments = """
def test():
    a = b
    return 3


"""


def test_strip_commments():
    statement = "if True: # a comment"
    stripped = strip_comments(statement)
    assert stripped == "if True:"
    assert without_comments == strip_comments(with_comments)
    # other method -- not reliable when tab characters are present
    assert stringify(tokenize(statement), remove_comments=True) == stripped
    assert without_comments == stringify(tokenize(with_comments), remove_comments=True)


def test_bracket_stack():
    bracket_stack = BracketStack()
    assert bracket_stack.is_empty()

    tokens = tokenize(" a b c ({ d []})")
    for token in tokens:
        if token.is_bracket():
            result = bracket_stack.add(token)
            if token.is_open_bracket():
                assert not bracket_stack.is_empty()
                assert not result  # bracket appended
            else:
                assert result  # bracket popped
    assert bracket_stack.is_empty()
