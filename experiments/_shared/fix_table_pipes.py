r"""One-off: escape literal `|` characters inside `$|...|$` math blocks in
LEARNINGS.md.

The earlier version of this script over-matched: a regex like
`\$[^$\n]*\|[^$\n]*\$` would match across TWO separate math blocks if there
was a `|` between them (e.g., `$\chi(H_1)$ | Half 2 | $\chi(H_2)$` got
interpreted as one math block `$ | Half 2 | $`, causing the table-separator
pipes between cells to be escaped — breaking the table.

This version uses a targeted regex `\$\|([^|$\n]+)\|\$` that only matches
the specific pattern `$|<token>|$` (dollar, pipe, non-pipe content, pipe,
dollar). Safe for table cells.
"""

import pathlib
import re

p = pathlib.Path(__file__).resolve().parents[1] / "LEARNINGS.md"
text = p.read_text(encoding="utf-8")

def fix(m):
    inner = m.group(1)
    return r"$\|" + inner + r"\|$"

# Match $|...|$ where the inner part has no pipes, dollars, or newlines.
pattern = r"\$\|([^|$\n]+)\|\$"
new_text, n = re.subn(pattern, fix, text)
p.write_text(new_text, encoding="utf-8")
print(f"rewrote {p}: {n} substitutions")
