r"""One-off: reverse the order of L1..LN entries in LEARNINGS.md.

Newest entries should appear at the top so the file reads "what landed most
recently first". Keeps the header, reverses entries, drops the now-stale
"no further entries yet" footer.
"""

import pathlib
import re

p = pathlib.Path(__file__).resolve().parents[1] / "LEARNINGS.md"
text = p.read_text(encoding="utf-8")

# Header is everything up to the first "### L1." line.
m = re.search(r"^### L\d+\.", text, re.MULTILINE)
assert m, "no L1 entry found"
header = text[: m.start()]

# Split on "### L<num>." occurrences. Each match starts an entry block.
entry_starts = [m.start() for m in re.finditer(r"^### L\d+\.", text[m.start():], re.MULTILINE)]
entry_starts = [s + m.start() for s in entry_starts]
entry_starts.append(len(text))

entries = []
for i in range(len(entry_starts) - 1):
    block = text[entry_starts[i]:entry_starts[i+1]]
    entries.append(block)

# The last entry may include the "no further entries yet" footer. Strip it.
if entries:
    last = entries[-1]
    footer_match = re.search(r"\n\(no further entries yet;.*?\)\s*\Z", last, re.DOTALL)
    if footer_match:
        entries[-1] = last[:footer_match.start()].rstrip() + "\n\n"

# Reverse so newest-first.
entries.reverse()

# Update header: replace the format note to indicate newest-first ordering.
header_lines = header.splitlines(keepends=True)
new_header_lines = []
for line in header_lines:
    if line.startswith("Format: one entry per finding."):
        new_header_lines.append(
            "Format: one entry per finding. **Newest entries at the top.** "
            "Lead with the finding, then context.\n"
        )
    else:
        new_header_lines.append(line)
new_header = "".join(new_header_lines)

# Reassemble.
out = new_header + "".join(entries)
# Ensure file ends with a newline.
if not out.endswith("\n"):
    out += "\n"

p.write_text(out, encoding="utf-8")
print(f"rewrote {p} with {len(entries)} entries in reverse order")
