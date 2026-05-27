r"""One-off: escape literal `|` characters inside `$...$` math blocks in
LEARNINGS.md.

Markdown tables interpret `|` as a column separator. A cell containing
`$|V|$` is read as TWO pipes worth of cell boundaries, which breaks the
column count and corrupts the separator row rendering. The fix is to write
`$\|V\|$` (escaped pipes in math mode).
"""

import pathlib
import re

p = pathlib.Path(__file__).resolve().parents[1] / "LEARNINGS.md"
text = p.read_text(encoding="utf-8")

def fix(m):
    inner = m.group(1)
    return "$" + inner.replace("|", r"\|") + "$"

# Match $...$ blocks (single-dollar inline math) that contain at least one |.
new_text = re.sub(r"\$([^\$\n]*\|[^\$\n]*)\$", fix, text)

p.write_text(new_text, encoding="utf-8")
remaining = re.findall(r"\$[^\$\n]*\|[^\$\n]*\$", new_text)
print(f"rewrote {p}; remaining unfixed: {len(remaining)}")
