from pathlib import Path

from token_utils import (
    generate_tokens,
    tokenize,
    make_fake_token,
    get_physical_lines,
    get_logical_lines,
    get_significant_tokens,
    dedent,
    pairwise,
    sliding_window,
    BracketStack,
    OrphanedClosingBracket,
    MismatchedBrackets,
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
lines2 = get_physical_lines(source2)
lines3 = get_physical_lines(source3)


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


def test_stringify_remove_comments():
    assert (
        stringify(list(generate_tokens(with_comments)), remove_comments=True)
        == without_comments
    )


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


def test_orphaned_bracket():
    stack = BracketStack()
    tokens = tokenize("a ]")
    bracket = tokens[1]
    exception_raised = False
    for token in tokens:
        if token.is_bracket():
            try:
                stack.add(token)
            except OrphanedClosingBracket as e:
                exception_raised = True
                assert e.bracket == bracket
    assert exception_raised


def test_mismatched_brackets():
    stack = BracketStack()
    tokens = tokenize("( ]")
    opened = tokens[0]
    close = tokens[1]
    exception_raised = False
    stack.add(opened)
    try:
        stack.add(close)
    except MismatchedBrackets as e:
        exception_raised = True
        assert e.open_bracket == opened
        assert e.close_bracket == close
    assert exception_raised


def test_decorator_example():
    # Not a unit test, but it will do for now
    current_path = Path(__file__)
    current_dir = current_path.parent
    target = current_dir / "decorator_example_out.txt"
    with open(target, "r") as f:
        expected = f.read()
    from . import add_decorator

    assert add_decorator.output == expected


def test_nobreak_example():
    # not a unit test but it will do for now
    current_path = Path(__file__)
    current_dir = current_path.parent
    target = current_dir / "nobreak_out.txt"
    with open(target, "r") as f:
        expected = f.read()
    from . import nobreak

    assert nobreak.output == expected


def test_factorial_example():
    from .factorial import make_factorial

    assert make_factorial("3!") == "factorial(3)"
    assert make_factorial("(2+3)!") == "factorial(2+3)"


def test_get_significant():
    source = "A test # comment"
    assert get_logical_lines(source)[0][:-1] == get_significant_tokens(source)
    assert len(get_significant_tokens(source)) == 2
    assert get_significant_tokens("# Only a comment") == []
