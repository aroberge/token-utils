"""This is meant to check that roundtrips (tokenize/untokenize) are
working correctly.

Most of these tests have been adapted from https://github.com/myint/untokenize.
"""

from token_utils import (
    tokenize,
    untokenize,
    get_significant_tokens,
    get_lines,
    get_stripped_lines,
    untokenize_lines_of_tokens,
)


def check_all(source):
    # "remove_comments" simply does not include them as tokens.
    assert untokenize(tokenize(source)) == source
    assert untokenize(get_significant_tokens(source, remove_comments=False)) == source
    assert untokenize_lines_of_tokens(get_lines(source)) == source
    assert (
        untokenize_lines_of_tokens(get_stripped_lines(source, remove_comments=False))
        == source
    )


def check(source):
    assert source == untokenize(tokenize(source))


def check_lines(source):
    assert source == untokenize_lines_of_tokens(source)


complex_source = '''

def zap():

    """Hello zap.

  """; 1


    x \t= \t\t  \t 1


'''


def test_complex_source():
    check_all(complex_source)


tab_indentation = """
if True:
\tdef zap():
\t\tx \t= \t\t  \t 1
"""


def test_untokenize_with_tab_indentation():
    check_all(tab_indentation)


backslash_in_comment = r'''
def foo():
    """Hello foo."""
    def zap(): bar(1) # \
'''


def test_untokenize_with_backslash_in_comment():
    check_all(backslash_in_comment)


escaped_newline = r'''def foo():
    """Hello foo."""
    x = \
            1
'''


def test_untokenize_with_escaped_newline():
    check_all(escaped_newline)


def test_cpython_bug_35107():
    # Checking https://bugs.python.org/issue35107#msg328884
    check_all("#")
    check_all("#\n")


def test_last_line_empty():
    """If the last line contains only space characters with no newline
    Python's tokenizer drops this content. To ensure that the
    tokenize-untokenize returns the original value, we have introduced
    a fix in our utility functions"""

    source = "a\n  "
    source2 = "a\n\t"
    check_all(source)
    check_all(source2)


def test_bad_dedent():
    """Instead of raising and IndentationError, we should have a special
    token inserted, allowing us to reconstruct the source."""
    source = """
    def test():
        a = b
       c = d
        e = f
    """
    check_all(source)


def test_problematic_newline():
    """When modifying Python's tokenize, I accidently added a
    string attribute to "NEWLINE" token, but all the existing
    tests passed even though this caused a bug. This test is to
    ensure that this bug does not happen again!
    """
    source = "2n"
    assert untokenize(tokenize(source)) == source
    #
    # test inserting non-token
    tokens = tokenize(source)
    new_tokens = []
    for tok in tokens:
        new_tokens.append(tok)
        if tok.is_number():
            new_tokens.append("*")
    assert untokenize(new_tokens) == "2*n"


def test_py_tokenize():
    """Complex example!"""
    from token_utils import py_tokenize

    with open(py_tokenize.__file__, "r") as f:
        source = f.read()
    assert untokenize(tokenize(source)) == source


def test_unterminated_string():
    source = "name = 'Bob "
    assert untokenize(tokenize(source)) == source


unclosed_triple_quoted_string = """
a = b  # see next line
    '''  this is meant to be a long
comment string but it never terminated.
"""


def test_unterminated_triple_quoted_string():
    assert (
        untokenize(tokenize(unclosed_triple_quoted_string))
        == unclosed_triple_quoted_string
    )


def test_invalid_octal():
    # See https://github.com/friendly-traceback/friendly-traceback/issues/242
    source = "b = 0o1876 + 0o2"
    assert untokenize(tokenize(source)) == source
    source = "a = 0o23 + 0O2987"
    assert untokenize(tokenize(source)) == source


def test_non_printable_character():
    source = 'print\x17("Hello")'
    assert untokenize(tokenize(source)) == source
