# nobreak.py
from token_utils import get_logical_lines, untokenize, IndentStack

with open("nobreak.txt", "r") as f:
    source = f.read()

new_lines = []
stack = IndentStack()
stack.add_same_indent_keyword("nobreak")

for line in get_logical_lines(source):
    top = stack.update(line)
    if top is None:  # this line does not introduce an indented block
        new_lines.append(line)
        continue

    if line[0] == "nobreak" and top.is_in(["for", "while"]):
        line[0].string = "else"  # modify in place

    new_lines.append(line)

print(untokenize(new_lines))
