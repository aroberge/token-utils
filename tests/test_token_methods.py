# Most of the following tests are trivial but they are there in
# case we make a typo when changing code. It happens...


from token_utils import tokenize


def test_contains():
    tokens = tokenize("name = 'Bob'")
    assert "name" in tokens[0]
    assert "Bob" in tokens[2]
    assert "'Bob'" in tokens[2]


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


def test_is_f_string():
    tokens = tokenize("f'{something}' 'other'")
    assert tokens[0].is_string()
    assert tokens[0].is_f_string()
    assert tokens[1].is_string()
    assert not tokens[1].is_f_string()


def test_is_float():
    tokens = tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert tokens[0].is_float()
    assert tokens[2] == "2.0j"
    assert not tokens[2].is_float()
    assert tokens[4] == "1"
    assert not tokens[4].is_float()


def test_is_in():
    tokens = tokenize("2+4-5")
    for token in tokens:
        if not token.string.strip():
            continue
        assert token.is_in(["2", "+", "4", "-", "5"])
        assert not token.is_in(["1", "3", "*", "/"])


def test_is_identifier():
    tokens = tokenize("def test")
    assert tokens[0] == "def"
    assert not tokens[0].is_identifier()
    assert tokens[1] == "test"
    assert tokens[1].is_identifier()


def test_immediately_before_and_after():
    tokens = tokenize("**/ =")
    assert tokens[0] == "**"
    assert tokens[1] == "/"
    assert tokens[2] == "="
    assert tokens[0].is_immediately_before(tokens[1])
    assert tokens[1].is_immediately_after(tokens[0])
    assert not tokens[1].is_immediately_before(tokens[2])
    assert not tokens[2].is_immediately_after(tokens[1])


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


def test_is_string():
    tokens = tokenize("name = 'Bob'")
    assert not tokens[0].is_string()
    assert tokens[2].is_string()


def test_is_unclosed_string():
    tokens = tokenize("' a")
    assert tokens[0].is_unclosed_string()

    tokens = tokenize("'''   ")
    assert tokens[0].is_unclosed_string()
