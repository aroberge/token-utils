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


# Many of the following tests are trivial but they are there in
# case we make a typo when changing code


def test_contains():
    token = tokenize("'Hello World!'")[0]
    assert token == "'Hello World!'"  # token define equality this way
    assert "Hello" in token


def test_len():
    tokens = tokenize("name = 'Albert'")
    assert tokens[0] == "name"
    assert len(tokens[0]) == 4
    assert tokens[1] == "="
    assert len(tokens[1]) == 1
    assert tokens[2] == "'Albert'"
    assert len(tokens[2]) == 8


def test_is_comment():
    tokens = tokenize("a # comment")
    assert not tokens[0].is_comment()
    assert tokens[0] == "a"
    assert tokens[1].is_comment()
    assert tokens[1] == "# comment"


def test_is_complex():
    tokens = tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert not tokens[0].is_complex()
    assert tokens[2] == "2.0j"
    assert tokens[2].is_complex()
    assert tokens[4] == "1"
    assert not tokens[4].is_complex()


def test_is_float():
    tokens = tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert tokens[0].is_float()
    assert tokens[2] == "2.0j"
    assert not tokens[2].is_float()
    assert tokens[4] == "1"
    assert not tokens[4].is_float()


def test_is_identifier():
    tokens = tokenize("def test")
    assert tokens[0] == "def"
    assert not tokens[0].is_identifier()
    assert tokens[1] == "test"
    assert tokens[1].is_identifier()


def test_is_integer():
    tokens = tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert not tokens[0].is_integer()
    assert tokens[2] == "2.0j"
    assert not tokens[2].is_integer()
    assert tokens[4] == "1"
    assert tokens[4].is_integer()


def test_is_keyword():
    tokens = tokenize("def test")
    assert tokens[0] == "def"
    assert tokens[0].is_keyword()
    assert tokens[1] == "test"
    assert not tokens[1].is_keyword()


def test_is_name():
    tokens = tokenize("def test")
    assert tokens[0] == "def"
    assert tokens[0].is_name()
    assert tokens[1] == "test"
    assert tokens[1].is_name()


def test_is_number():
    tokens = tokenize("1.0 + 2.0j - 1 + 0o123 + 0x1A")
    assert tokens[0] == "1.0"
    assert tokens[0].is_number()
    assert tokens[2] == "2.0j"
    assert tokens[2].is_number()
    assert tokens[4] == "1"
    assert tokens[4].is_number()
    assert tokens[6] == "0o123"
    assert tokens[6].is_number()
    assert tokens[8] == "0x1A"
    assert tokens[8].is_number()


def test_is_operator():
    tokens = tokenize("a = - 3")
    assert tokens[1] == "="
    assert tokens[1].is_operator()
    assert tokens[2] == "-"
    assert tokens[2].is_operator()
    assert not tokens[0].is_operator()
