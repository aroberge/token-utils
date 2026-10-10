from typing import Literal, Pattern
from _typeshed import Incomplete

import collections
from token_utils._token_plus import *
from token_utils.custom_warnings import TokenUtilsEOFWarning
from token_utils._token_plus import __all__

blank_re: Pattern[bytes]

class TokenInfo(collections.namedtuple("TokenInfo", "type string start end line")):
    def __repr__(self) -> Incomplete: ...
    @property
    def exact_type(self) -> Incomplete: ...

def group(*choices: Incomplete) -> Incomplete: ...
def any(*choices: Incomplete) -> Incomplete: ...
def maybe(*choices: Incomplete) -> Incomplete: ...

Whitespace: Literal["[ \\f\\t]*"] = r"[ \f\t]*"
Comment: Literal["#[^\\r\\n]*"] = r"#[^\r\n]*"
Ignore: Incomplete
Name: Literal["\\w+"] = r"\w+"
Hexnumber: Literal["0[xX](?:_?[0-9a-fA-F])+"] = r"0[xX](?:_?[0-9a-fA-F])+"
Binnumber: Literal["0[bB](?:_?[01])+"] = r"0[bB](?:_?[01])+"
Octnumber: Literal["0[oO](?:_?[0-7])+"] = r"0[oO](?:_?[0-7])+"
Decnumber: Literal["(?:0(?:_?0)*|[1-9](?:_?[0-9])*)"] = (
    r"(?:0(?:_?0)*|[1-9](?:_?[0-9])*)"
)
Intnumber: Incomplete
Exponent: Literal["[eE][-+]?[0-9](?:_?[0-9])*"] = r"[eE][-+]?[0-9](?:_?[0-9])*"
Pointfloat: Incomplete
Expfloat: str
Floatnumber: Incomplete
Imagnumber: Incomplete
Number: Incomplete
StringPrefix: Incomplete
Single: Literal["[^'\\\\]*(?:\\\\.[^'\\\\]*)*'"] = r"[^'\\]*(?:\\.[^'\\]*)*'"
Double: Literal['[^"\\\\]*(?:\\\\.[^"\\\\]*)*"'] = r'[^"\\]*(?:\\.[^"\\]*)*"'
Single3: Literal["[^'\\\\]*(?:(?:\\\\.|'(?!''))[^'\\\\]*)*'''"] = (
    r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
)
Double3: Literal['[^"\\\\]*(?:(?:\\\\.|"(?!""))[^"\\\\]*)*"""'] = (
    r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
)
Triple: Incomplete
String: Incomplete
Special: Incomplete
Funny: Incomplete
PlainToken: Incomplete
Token: Incomplete
ContStr: Incomplete
PseudoExtras: Incomplete
PseudoToken: Incomplete
contline: str | None
endpats: Incomplete
single_quoted: Incomplete
triple_quoted: Incomplete
tabsize: Literal[8] = 8

def generate_tokens(readline: Incomplete) -> Incomplete: ...

BAD_DEDENT: Literal[-1]
UNCL_SINGLE: Literal[-2]
UNCL_TRIPLE: Literal[-3]
FAKE_TOKEN: Literal[-4]
