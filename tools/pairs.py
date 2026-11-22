"""pairs.py: reviewer input, `>> id | JP / EN` for the entries under review with +-2 neighbours as context.

    python -X utf8 tools/pairs.py b026 [b027 ...]          # the ids of work/tl/bNNN.tsv
    python -X utf8 tools/pairs.py --file master_257BD4      # every English entry of one script file
    python -X utf8 tools/pairs.py ... --out work/qa/review/b026.txt

Master dialogue shows the page view (`<speaker>`, pages ` ‖ ` / ` || `); side tables show jp / en. Context lines
start with two spaces instead of `>>`. Long reviews: one batch (~150 entries) a reviewer read.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402


def row(e, mark):
    if batches.is_master(e):
        jp, en = batches.pages.jp_view(e["jp"], batches.NAMES), e.get("pages") or e.get("en", "")
    else:
        jp, en = e["jp"].replace("\n", "\\n"), e.get("en", "").replace("\n", "\\n")
    return f"{mark} {e['id']} | {jp}\n   EN: {en or '(JP kept)'}"


def pairs(ids):
    entries = batches.index()
    order = {}
    for path, _, doc in batches.docs():
        order[path.stem] = [e["id"] for e in doc]
    want = [i for i in ids if i in entries]
    out, shown = [], set()
    for i in want:
        seq = order[batches.file_of(entries[i])]
        k = seq.index(i)
        for j in seq[max(0, k - 2):k + 3]:
            if j in shown:
                continue
            shown.add(j)
            e = entries[j]
            if j != i and not (e.get("en") or j in want):
                continue
            out.append(row(e, ">>" if j in want else "  "))
    return "\n".join(out) + "\n"


def main(argv):
    if not argv:
        sys.exit(__doc__)
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    args = [a for k, a in enumerate(argv) if a != "--out" and (k == 0 or argv[k - 1] != "--out")]
    ids = []
    if args[0] == "--file":
        entries = batches.index()
        ids = [i for i, e in entries.items() if batches.file_of(e) == args[1] and e.get("en")]
    else:
        for b in args:
            ids += [r[0] for r in batches.read_tsv(batches.TL / f"{b}.tsv")]
    text = pairs(ids)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8", newline="\n")
        print(f"{out}: {text.count(chr(10) + '>>') + text.startswith('>>')} entries")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
