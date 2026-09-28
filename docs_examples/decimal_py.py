# decimal_py.py
#
# Example taken from Python's tokenize module documentation

from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from io import BytesIO


def float_to_decimal(s):  # changed name from Python's example
    result = []
    g = tokenize(BytesIO(s.encode("utf-8")).readline)  # tokenize the string
    for toknum, tokval, _, _, _ in g:
        if toknum == NUMBER and "." in tokval:  # replace NUMBER tokens
            result.extend(
                [(NAME, "Decimal"), (OP, "("), (STRING, repr(tokval)), (OP, ")")]
            )
        else:
            result.append((toknum, tokval))
    return untokenize(result).decode("utf-8")
