"""Print the release notes found in a pull request body (read from stdin).

The notes are the bullet list ("- " or "* " lines) that follows the first line
mentioning "release notes" or ending in "these notes:". Exits 1 if none found.
"""
import re
import sys

lines = sys.stdin.read().splitlines()
start = next((i for i, l in enumerate(lines)
              if re.search(r"release notes|these notes:\s*$", l, re.I)), None)
if start is None:
    sys.exit("no 'Release notes' line in the pull request body")
notes = []
for l in lines[start + 1:]:
    if re.match(r"\s*[-*] ", l):
        notes.append(l.rstrip())
    elif notes and l.strip():
        break
if not notes:
    sys.exit("no bullet list after the 'Release notes' line")
print("\n".join(notes))
