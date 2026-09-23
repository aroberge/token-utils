# token-utils

The purpose of token-utils is to simplify manipulations of tokens from
Python's [tokenize module](https://docs.python.org/3/library/tokenize.html).
One of its features is that, unlike Python's version, the following
is always guaranteed:

```python
from token_utils import tokenize, untokenize

source = "Arbitrary Python code here"

assert source == untokenize(tokenize(source))
```

Consider [this example from Python's standard library](https://docs.python.org/3/library/tokenize.html#examples):

```python
from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from io import BytesIO

def decistmt(s):
    result = []
    g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
    for toknum, tokval, _, _, _ in g:
        if toknum == NUMBER and '.' in tokval:  # replace NUMBER tokens
            result.extend([
                (NAME, 'Decimal'),
                (OP, '('),
                (STRING, repr(tokval)),
                (OP, ')')
            ])
        else:
            result.append((toknum, tokval))
    return untokenize(result).decode('utf-8')
```

Here's how you could achieve the same result with token-utils:

```python
from token_utils import tokenize, untokenize

def decistmt(source):
    tokens = token_utils.tokenize(source)
    for token in tokens:
        if token.is_number() and "." in token.string:
            token.string = f"Decimal('{token.string}')"
    return token_utils.untokenize(tokens)

```

See [the documentation](https://aroberge.github.io/token-utils/docs/html/) for more information
