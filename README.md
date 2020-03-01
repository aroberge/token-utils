# token-utils

This project consists of a single module which is extracted from the
[ideas](https://github.com/aroberge/ideas) package.
Its purpose is to simplify manipulations of tokens from
Python's [tokenize module](https://docs.python.org/3/library/tokenize.html).
One of its features is that, unlike Python's version, the following
is always guaranteed:

```python
from token_utils import tokenize, untokenize

source = "Arbitrary Python code here"

assert source == untokenize(tokenize(source))
```

See [ideas documentation](https://aroberge.github.io/ideas/docs/html/) for more information
