# view_stack.py
from token_utils import get_physical_lines, IndentStack, untokenize

with open("decorator_example.txt", "r") as f:
    source = f.read()
stack = IndentStack()

# It is highly preferable to use get_logical_lines as this example shows.
for line in get_physical_lines(source):
    print(
        f"{untokenize(line).rstrip():<25}",
        f".update() --> {str(stack.update(line)):<7}",
        "==> ",
        end=" ",
    )
    stack.print_stack()
