# inside_blocks.py
from token_utils import get_logical_lines, IndentStack, stringify

with open("decorator_example.txt", "r") as f:
    source = f.read()

stack = IndentStack()

for line in get_logical_lines(source):
    stack.update(line)
    first_token = line[0]
    inside_class = stack.is_token_in_named_block(first_token, "class")
    inside_def = stack.is_token_in_named_block(first_token, "def")
    print(
        f"{stringify(line).rstrip():20}",
        f"{inside_def=};",
        f"{inside_class=};",
        "  stack:",
        end=" ",
    )
    stack.print_stack()
