import token_utils

# Note: most of the tests involving untokenize have
# been adapted from https://github.com/myint/untokenize


def check(source):
    tokens = token_utils.tokenize(source)
    new_source = token_utils.untokenize(tokens)
    print(len(source), len(new_source))
    assert source == new_source


def check_lines(source):
    lines = token_utils.get_lines(source)
    tokens = []
    for line in lines:
        tokens.extend(line)
    assert source == token_utils.untokenize(tokens)


def test_untokenize():
    check('''

def zap():

    """Hello zap.

  """; 1


    x \t= \t\t  \t 1


''')


def test_untokenize_with_tab_indentation():
    check("""
if True:
\tdef zap():
\t\tx \t= \t\t  \t 1
""")


def test_untokenize_with_backslash_in_comment():
    check(r'''
def foo():
    """Hello foo."""
    def zap(): bar(1) # \
''')


def test_untokenize_with_escaped_newline():
    check(r'''def foo():
    """Hello foo."""
    x = \
            1
''')


def test_cpython_bug_35107():
    # Checking https://bugs.python.org/issue35107#msg328884
    check("#")
    check("#\n")


def test_last_line_empty():
    """If the last line contains only space characters with no newline
    Python's tokenizer drops this content. To ensure that the
    tokenize-untokenize returns the original value, we have introduced
    a fix in our utility functions"""

    source = "a\n  "
    source2 = "a\n\t"
    check(source)
    check(source2)

    check_lines(source)
    check_lines(source2)


def test_bad_dedent():
    """Instead of raising and IndentationError, we should have a special
    token inserted, allowing us to reconstruct the source."""
    source = """
    def test():
        a = b
       c = d
        e = f
    """
    check(source)

def test_problematic_newline():
    """When modifying Python's tokenize, I accidently added a
    string attribute to "NEWLINE" token. This test is to
    ensure that this does not happen again!
    """
    source = "2n"
    assert token_utils.untokenize(token_utils.tokenize(source)) == source
    #
    # test inserting non-token
    tokens = token_utils.tokenize(source)
    new_tokens = []
    for tok in tokens:
        new_tokens.append(tok)
        if tok.is_number():
            new_tokens.append("*")
    assert token_utils.untokenize(new_tokens) == "2*n"


source1 = "a = b"
source2 = "a = b # comment\n"
source3 = """
if True:
    a = b # comment
"""
tokens1 = token_utils.tokenize(source1)
tokens2 = token_utils.tokenize(source2)
lines3 = token_utils.get_lines(source3)


def test_first():
    assert token_utils.get_first(tokens1) == token_utils.get_first(tokens2)
    assert token_utils.get_first(tokens1) == "a"
    assert token_utils.get_first(tokens2, exclude_comment=False) == "a"
    assert token_utils.get_first_index(tokens1) == 0

    assert token_utils.get_first(lines3[2]) == "a"
    assert token_utils.get_first_index(lines3[2]) == 1


def test_last():
    assert token_utils.get_last(tokens1) == token_utils.get_last(tokens2)
    assert token_utils.get_last(tokens1) == "b"
    assert token_utils.get_last(tokens2, exclude_comment=False) == "# comment"
    assert token_utils.get_last_index(tokens1) == 2

    assert token_utils.get_last(lines3[2]) == "b"
    assert token_utils.get_last_index(lines3[2]) == 3
    assert token_utils.get_last_index(lines3[2], exclude_comment=False) == 4


def test_dedent():
    new_tokens = token_utils.dedent(lines3[2], 4)
    assert new_tokens == tokens2


def test_indent():
    new_tokens = token_utils.indent(tokens2, 4)
    new_line_a = token_utils.untokenize(new_tokens)
    new_line_b = token_utils.untokenize(lines3[2])
    assert new_line_a == new_line_b


def test_find_substring_index():
    assert token_utils.find_substring_index(source2, source3) == -1
    assert token_utils.find_substring_index(source3, source2) == 3


def test_self():
    with open(__file__, "r") as f:
        source = f.read()
    check(source)


# Many of the following tests are trivial but they are there in
# case we make a typo when changing code


def test_contains():
    token = token_utils.tokenize("'Hello World!'")[0]
    assert token == "'Hello World!'"  # token define equality this way
    assert "Hello" in token


def test_len():
    tokens = token_utils.tokenize("name = 'Albert'")
    assert tokens[0] == "name"
    assert len(tokens[0]) == 4
    assert tokens[1] == "="
    assert len(tokens[1]) == 1
    assert tokens[2] == "'Albert'"
    assert len(tokens[2]) == 8


def test_is_comment():
    tokens = token_utils.tokenize("a # comment")
    assert not tokens[0].is_comment()
    assert tokens[0] == "a"
    assert tokens[1].is_comment()
    assert tokens[1] == "# comment"


def test_is_complex():
    tokens = token_utils.tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert not tokens[0].is_complex()
    assert tokens[2] == "2.0j"
    assert tokens[2].is_complex()
    assert tokens[4] == "1"
    assert not tokens[4].is_complex()


def test_is_float():
    tokens = token_utils.tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert tokens[0].is_float()
    assert tokens[2] == "2.0j"
    assert not tokens[2].is_float()
    assert tokens[4] == "1"
    assert not tokens[4].is_float()


def test_is_identifier():
    tokens = token_utils.tokenize("def test")
    assert tokens[0] == "def"
    assert not tokens[0].is_identifier()
    assert tokens[1] == "test"
    assert tokens[1].is_identifier()


def test_is_integer():
    tokens = token_utils.tokenize("1.0 + 2.0j - 1")
    assert tokens[0] == "1.0"
    assert not tokens[0].is_integer()
    assert tokens[2] == "2.0j"
    assert not tokens[2].is_integer()
    assert tokens[4] == "1"
    assert tokens[4].is_integer()


def test_is_keyword():
    tokens = token_utils.tokenize("def test")
    assert tokens[0] == "def"
    assert tokens[0].is_keyword()
    assert tokens[1] == "test"
    assert not tokens[1].is_keyword()


def test_is_name():
    tokens = token_utils.tokenize("def test")
    assert tokens[0] == "def"
    assert tokens[0].is_name()
    assert tokens[1] == "test"
    assert tokens[1].is_name()


def test_is_number():
    tokens = token_utils.tokenize("1.0 + 2.0j - 1 + 0o123 + 0x1A")
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
    tokens = token_utils.tokenize("a = - 3")
    assert tokens[1] == "="
    assert tokens[1].is_operator()
    assert tokens[2] == "-"
    assert tokens[2].is_operator()
    assert not tokens[0].is_operator()
