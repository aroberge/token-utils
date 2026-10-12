# add_decorator.py

from pathlib import Path

from token_utils import get_logical_lines, IndentStack, untokenize, stringify

current_path = Path(__file__)
current_dir = current_path.parent
target = current_dir / "decorator_example.txt"

with open(target, "r") as f:
    source = f.read()

stack = IndentStack()
new_lines = []
for line in get_logical_lines(source):
    stack.update(line)
    first_token = line[0]
    if first_token == "def" and not stack.is_token_in_named_block(first_token, "class"):
        new_lines.append([" " * first_token.indentation() + "@decorator\n"])

    new_lines.append(line)

output = stringify(new_lines)
