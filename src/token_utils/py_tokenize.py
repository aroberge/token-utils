"""Tokenization help for Python programs.

This has been adapted from Python 3.11 tokenize.py
It has been mostly copied almost exactly except that anything
about "untokenizing" has been removed as we rely on our
own version. We've also removed anything related to encoding as
it is  not needed.

Anything in this module should NOT be called directly from
your code.
"""

import collections
import functools
import itertools as _itertools
import re
from token_utils.token_plus import *

# prevent accidently importing * from here as names might conflict with our own
from token_utils.token_plus import __all__

blank_re = re.compile(rb"^[ \t\f]*(?:[#\r\n]|$)", re.ASCII)


class TokenInfo(collections.namedtuple("TokenInfo", "type string start end line")): ...


def group(*choices):
    return "(" + "|".join(choices) + ")"


def any(*choices):
    return group(*choices) + "*"


def maybe(*choices):
    return group(*choices) + "?"


# Note: we use unicode matching for names ("\w") but ascii matching for
# number literals.
Whitespace = r"[ \f\t]*"
Comment = r"#[^\r\n]*"
Ignore = Whitespace + any(r"\\\r?\n" + Whitespace) + maybe(Comment)
Name = r"\w+"

Hexnumber = r"0[xX](?:_?[0-9a-fA-F])+"
Binnumber = r"0[bB](?:_?[01])+"
Octnumber = r"0[oO](?:_?[0-7])+"
Decnumber = r"(?:0(?:_?0)*|[1-9](?:_?[0-9])*)"
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r"[eE][-+]?[0-9](?:_?[0-9])*"
Pointfloat = group(
    r"[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?", r"\.[0-9](?:_?[0-9])*"
) + maybe(Exponent)
Expfloat = r"[0-9](?:_?[0-9])*" + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r"[0-9](?:_?[0-9])*[jJ]", Floatnumber + r"[jJ]")
Number = group(Imagnumber, Floatnumber, Intnumber)


# Return the empty string, plus all of the valid string prefixes.
def _all_string_prefixes():
    # The valid string prefixes. Only contain the lower case versions,
    #  and don't contain any permutations (include 'fr', but not
    #  'rf'). The various permutations will be generated.
    _valid_string_prefixes = ["b", "r", "u", "f", "br", "fr"]
    # if we add binary f-strings, add: ['fb', 'fbr']
    result = {""}
    for prefix in _valid_string_prefixes:
        for t in _itertools.permutations(prefix):
            # create a list with upper and lower versions of each
            #  character
            for u in _itertools.product(*[(c, c.upper()) for c in t]):
                result.add("".join(u))
    return result


@functools.lru_cache
def _compile(expr):
    return re.compile(expr, re.UNICODE)


# Note that since _all_string_prefixes includes the empty string,
#  StringPrefix can be the empty string (making it optional).
StringPrefix = group(*_all_string_prefixes())

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
Triple = group(StringPrefix + "'''", StringPrefix + '"""')
# Single-line ' or " string.
String = group(
    StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
    StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"',
)

# Sorting in reverse order puts the long operators before their prefixes.
# Otherwise if = came before ==, == would get recognized as two instances
# of =.
Special = group(*map(re.escape, sorted(EXACT_TOKEN_TYPES, reverse=True)))
Funny = group(r"\r?\n", Special)

PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken

# First (or only) line of ' or " string.
ContStr = group(
    StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*" + group("'", r"\\\r?\n"),
    StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*' + group('"', r"\\\r?\n"),
)
PseudoExtras = group(r"\\\r?\n|\Z", Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)

# For a given string prefix plus quotes, endpats maps it to a regex
#  to match the remainder of that string. _prefix can be empty, for
#  a normal single or triple quoted string (with no prefix).
endpats = {}
for _prefix in _all_string_prefixes():
    endpats[_prefix + "'"] = Single
    endpats[_prefix + '"'] = Double
    endpats[_prefix + "'''"] = Single3
    endpats[_prefix + '"""'] = Double3
del _prefix

# A set of all of the single and triple quoted string prefixes,
#  including the opening quotes.
single_quoted = set()
triple_quoted = set()
for t in _all_string_prefixes():
    for u in (t + '"', t + "'"):
        single_quoted.add(u)
    for u in (t + '"""', t + "'''"):
        triple_quoted.add(u)
del t, u

tabsize = 8


def generate_tokens(readline):
    """Tokenize a source reading Python code as unicode strings.

    It accepts a readline-like method which is called repeatedly to get the
    next line of input (or "" for EOF).  It generates 5-tuples with these
    members:

        the token type (see token.py)
        the token (a string)
        the starting (row, column) indices of the token (a 2-tuple of ints)
        the ending (row, column) indices of the token (a 2-tuple of ints)
        the original line (string)

    It is designed to match the working of the Python tokenizer exactly, except
    that it produces COMMENT tokens for comments and gives type OP for all
    operators.
    """
    lnum = parenlev = continued = 0
    numchars = "0123456789"
    contstr, needcont = "", 0
    contline = None
    indents = [0]

    last_line = ""
    line = ""
    unterminated_triple = False
    while True:  # loop over lines in stream
        try:
            # We capture the value of the line variable here because
            # readline uses the empty string '' to signal end of input,
            # hence `line` itself will always be overwritten at the end
            # of this loop.
            last_line = line
            line = readline()
        except StopIteration:
            line = ""

        lnum += 1
        pos, max = 0, len(line)

        if contstr:  # continued string
            if not line:
                end = len(contline.split("\n")[-1])
                print("ERROR: Unterminated triple quoted string.")
                unterminated_triple = True
                yield TokenInfo(UNCL_TRIPLE, contstr, strstart, (lnum, end), contline)
                break
            endmatch = endprog.match(line)
            if endmatch:
                pos = end = endmatch.end(0)
                yield TokenInfo(
                    STRING, contstr + line[:end], strstart, (lnum, end), contline + line
                )
                contstr, needcont = "", 0
                contline = None
            elif needcont and line[-2:] != "\\\n" and line[-3:] != "\\\r\n":
                current_str = contstr + line
                if current_str.strip():
                    if current_str in ("'", '"'):
                        yield TokenInfo(
                            UNCL_SINGLE,
                            current_str,
                            strstart,
                            (lnum, len(line)),
                            contline,
                        )
                    else:
                        yield TokenInfo(
                            ERRORTOKEN,
                            current_str,
                            strstart,
                            (lnum, len(line)),
                            contline,
                        )
                contstr = ""
                contline = None
                continue
            else:
                contstr = contstr + line
                contline = contline + line
                continue

        elif parenlev == 0 and not continued:  # new statement
            if not line:
                break
            column = 0
            while pos < max:  # measure leading whitespace
                if line[pos] == " ":
                    column += 1
                elif line[pos] == "\t":
                    column = (column // tabsize + 1) * tabsize
                elif line[pos] == "\f":
                    column = 0
                else:
                    break
                pos += 1
            if pos == max:
                break

            if line[pos] in "#\r\n":  # skip comments or blank lines
                if line[pos] == "#":
                    comment_token = line[pos:].rstrip("\r\n")
                    yield TokenInfo(
                        COMMENT,
                        comment_token,
                        (lnum, pos),
                        (lnum, pos + len(comment_token)),
                        line,
                    )
                    pos += len(comment_token)

                yield TokenInfo(NL, line[pos:], (lnum, pos), (lnum, len(line)), line)
                continue

            if column > indents[-1]:  # count indents or dedents
                indents.append(column)
                yield TokenInfo(INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
            while column < indents[-1]:
                if column not in indents:
                    yield TokenInfo(
                        BAD_DEDENT, line[:pos], (lnum, 0), (lnum, pos), line
                    )
                    break
                indents = indents[:-1]

                yield TokenInfo(DEDENT, "", (lnum, pos), (lnum, pos), line)

        else:  # continued statement
            if not line:
                end = len(contline.split("\n")[-1])
                print("ERROR: Unterminated triple quoted string.")
                unterminated_triple = True
                yield TokenInfo(UNCL_TRIPLE, contstr, strstart, (lnum, end), contline)
                break
            continued = 0

        while pos < max:
            pseudomatch = _compile(PseudoToken).match(line, pos)
            if pseudomatch:  # scan for tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                if start == end:
                    continue
                token, initial = line[start:end], line[start]

                if initial in numchars or (  # ordinary number
                    initial == "." and token != "." and token != "..."
                ):
                    yield TokenInfo(NUMBER, token, spos, epos, line)
                elif initial in "\r\n":
                    if parenlev > 0:
                        yield TokenInfo(NL, token, spos, epos, line)
                    else:
                        yield TokenInfo(NEWLINE, token, spos, epos, line)

                elif initial == "#":
                    assert not token.endswith("\n")
                    yield TokenInfo(COMMENT, token, spos, epos, line)

                elif token in triple_quoted:
                    endprog = _compile(endpats[token])
                    endmatch = endprog.match(line, pos)
                    if endmatch:  # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        yield TokenInfo(STRING, token, spos, (lnum, pos), line)
                    else:
                        strstart = (lnum, start)  # multiple lines
                        contstr = line[start:]
                        contline = line
                        break

                # Check up to the first 3 chars of the token to see if
                #  they're in the single_quoted set. If so, they start
                #  a string.
                # We're using the first 3, because we're looking for
                #  "rb'" (for example) at the start of the token. If
                #  we switch to longer prefixes, this needs to be
                #  adjusted.
                # Note that initial == token[:1].
                # Also note that single quote checking must come after
                #  triple quote checking (above).
                elif (
                    initial in single_quoted
                    or token[:2] in single_quoted
                    or token[:3] in single_quoted
                ):
                    if token[-1] == "\n":  # continued string
                        strstart = (lnum, start)
                        # Again, using the first 3 chars of the
                        #  token. This is looking for the matching end
                        #  regex for the correct type of quote
                        #  character. So it's really looking for
                        #  endpats["'"] or endpats['"'], by trying to
                        #  skip string prefix characters, if any.
                        endprog = _compile(
                            endpats.get(initial)
                            or endpats.get(token[1])
                            or endpats.get(token[2])
                        )
                        contstr, needcont = line[start:], 1
                        contline = line
                        break
                    else:  # ordinary string
                        yield TokenInfo(STRING, token, spos, epos, line)

                elif initial.isidentifier():  # ordinary name
                    yield TokenInfo(NAME, token, spos, epos, line)
                elif initial == "\\":  # continued stmt
                    continued = 1
                else:
                    if initial in "([{":
                        parenlev += 1
                    elif initial in ")]}":
                        parenlev -= 1
                    yield TokenInfo(OP, token, spos, epos, line)
            else:
                current_char = line[pos]
                if current_char.strip():
                    if current_char in ("'", '"'):
                        yield TokenInfo(
                            UNCL_SINGLE,
                            line[pos],
                            (lnum, pos),
                            (lnum, pos + 1),
                            line,
                        )
                    else:
                        yield TokenInfo(
                            ERRORTOKEN, line[pos], (lnum, pos), (lnum, pos + 1), line
                        )
                pos += 1

    # TODO: see if we can remove this!!!
    # Add an implicit NEWLINE if the input doesn't end in one
    if not unterminated_triple:
        if (
            last_line
            and last_line[-1] not in "\r\n"
            and not last_line.strip().startswith("#")
        ):
            yield TokenInfo(
                NEWLINE,
                "",
                (lnum - 1, len(last_line)),
                (lnum - 1, len(last_line) + 1),
                last_line,
            )
        yield TokenInfo(ENDMARKER, "", (lnum, 0), (lnum, 0), "")
