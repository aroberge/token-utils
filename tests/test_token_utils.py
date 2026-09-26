from token_utils import (
    tokenize,
    get_lines,
    get_first,
    get_last,
    get_first_index,
    get_last_index,
    indent,
    dedent,
    untokenize,
    find_substring_index,
    strip_comments,
)

source1 = "a = b"
source2 = "a = b # comment\n"
source3 = """
if True:
    a = b # comment
"""
tokens1 = tokenize(source1)
tokens2 = tokenize(source2)
lines3 = get_lines(source3)


def test_first():
    assert get_first(tokens1) == get_first(tokens2)
    assert get_first(tokens1) == "a"
    assert get_first(tokens2, exclude_comment=False) == "a"
    assert get_first_index(tokens1) == 0

    assert get_first(lines3[2]) == "a"
    assert get_first_index(lines3[2]) == 1


def test_last():
    assert get_last(tokens1) == get_last(tokens2)
    assert get_last(tokens1) == "b"
    assert get_last(tokens2, exclude_comment=False) == "# comment"
    assert get_last_index(tokens1) == 2

    assert get_last(lines3[2]) == "b"
    assert get_last_index(lines3[2]) == 3
    assert get_last_index(lines3[2], exclude_comment=False) == 4


def test_dedent():
    new_tokens = dedent(lines3[2], 4)
    assert new_tokens == tokens2


def test_indent():
    new_tokens = indent(tokens2, 4)
    new_line_a = untokenize(new_tokens)
    new_line_b = untokenize(lines3[2])
    assert new_line_a == new_line_b


def test_find_substring_index():
    assert find_substring_index(source2, source3) == -1
    assert find_substring_index(source3, source2) == 3


with_comments = """
def test():   # a good function
    a = b     # fantastic mathematical operation
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
