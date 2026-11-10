"""Simple duplicate-code detector (window of consecutive normalised lines)."""
import re
from collections import defaultdict

WINDOW = 4
_TRIVIAL = {"else:", "try:", "finally:", "pass", "break", "continue", "return", ")", "]", "}"}


def _normalise(source):
    """Return [(line_no, normalised_text)] for meaningful lines only."""
    out = []
    for no, raw in enumerate(source.splitlines(), start=1):
        text = re.sub(r"#.*$", "", raw).strip()
        if not text or text in _TRIVIAL or text.startswith(("import ", "from ")):
            continue
        out.append((no, re.sub(r"\s+", " ", text)))
    return out


def find_duplicates(source, window=WINDOW):
    """Return (ratio, blocks).

    ratio  -- share of meaningful lines that sit in a repeated block
    blocks -- list of lists of line numbers, one list per repeated block
    """
    lines = _normalise(source)
    if len(lines) < window:
        return 0.0, []
    seen = defaultdict(list)
    for i in range(len(lines) - window + 1):
        key = tuple(text for _, text in lines[i:i + window])
        seen[key].append(i)
    marked, blocks = set(), []
    for positions in seen.values():
        if len(positions) < 2:
            continue
        for start in positions:
            marked.update(range(start, start + window))
        blocks.append([lines[p][0] for p in positions])
    return len(marked) / len(lines), blocks
