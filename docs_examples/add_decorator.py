# add_decorator.py

from token_utils import get_logical_lines, get_physical_lines, IndentStack, untokenize

with open("decorator_example.txt", "r") as f:
    source = f.read()

stack = IndentStack()
new_lines = []

# Usually, we'd need to use get_logical_lines,
# but since all logical lines correspond to a single physical lines
# it is safe to do so here
for line in get_physical_lines(source):
    stack.update(line)
    first_token = line[0]
    if first_token == "def" and not stack.is_token_in_named_block(first_token, "class"):
        new_lines.append([" " * first_token.indentation() + "@decorator\n"])
    new_lines.append(line)

print(untokenize(new_lines))
print("------\nSame example with logical lines instead:")

new_lines = []
for line in get_logical_lines(source):
    stack.update(line)
    first_token = line[0]
    if first_token == "def" and not stack.is_token_in_named_block(first_token, "class"):
        new_lines.append([" " * first_token.indentation() + "@decorator\n"])
    new_lines.append(line)

print(untokenize(new_lines))
