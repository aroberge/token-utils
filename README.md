# token-utils

Installation: `pip install token-utils`.

The purpose of token-utils is to simplify manipulations of tokens normally
obtaind from Python's [tokenize module](https://docs.python.org/3/library/tokenize.html).

To get an idea of the simplicity of using token-utils,
consider [this example from Python's own documentation](https://docs.python.org/3/library/tokenize.html#examples) which substitute Decimals for floats in a string of statements:

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
    tokens = tokenize(source)
    for token in tokens:
        if token.is_float():
            token.string = f"Decimal('{token.string}')"
    return untokenize(tokens)
```

See [the documentation](https://aroberge.github.io/token-utils/docs/html/) for more information.
