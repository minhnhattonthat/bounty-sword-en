"""Fit-pass helper (D12): for each widow page in a `batches.py widows` TSV, print the page, its wrapped lines and
the sentence-boundary `{next}` splits whose boxes each fit 3 lines. It only suggests: the fix rows are written by
hand (`work/tl/fitNN.fix.tsv`, `id<TAB>page<TAB>new page`).

    python -X utf8 tools/fit_hint.py work/tl/widows.tsv [--from N] [--count N]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pages  # noqa: E402

BOUNDARY = re.compile(r"(?:\.\.\.|[.!?])['\"]? ")


def boxes(text):
    """Wrapped boxes of a page as the build lays it out (quotes like the JP)."""
    q = text.startswith('"') and text.endswith('"')
    body = text[1:-1] if q else text
    out = []
    for seg in body.split("{next}"):
        lines = pages.wrap(seg.strip(), "「" if q else "", " " if q else "", pages.px("」") if q else 0)
        out += [lines[i:i + pages.LINES] for i in range(0, len(lines), pages.LINES)]
    return out


def splits(text):
    """Pages with one `{next}` at a sentence end where every box holds 3 lines or fewer."""
    if "{next}" in text:
        return []
    found = []
    for m in BOUNDARY.finditer(text):
        cand = text[:m.end()].rstrip() + "{next}" + text[m.end():]
        if all(len(b) <= pages.LINES for b in boxes(cand)) and len(boxes(cand)) == 2:
            found.append(cand)
    return found


def main(argv):
    src = Path(argv[0])
    start = int(argv[argv.index("--from") + 1]) if "--from" in argv else 0
    count = int(argv[argv.index("--count") + 1]) if "--count" in argv else 10 ** 6
    rows = [ln.split("\t") for ln in src.read_text(encoding="utf-8").splitlines() if ln.count("\t") >= 3]
    for k, (eid, n, jp, en) in enumerate(rows[start:start + count], start):
        bx = boxes(en)
        tail = " / ".join(" ".join(b) for b in bx[1:])
        print(f"#{k} {eid} p{n} lines={sum(map(len, bx))} chars={len(en)} tail={tail!r}")
        print(f"  JP {jp}")
        print(f"  EN {en}")
        for c in splits(en):
            print(f"  SPLIT {c}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
