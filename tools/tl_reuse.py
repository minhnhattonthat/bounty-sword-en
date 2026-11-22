"""Reuse English for batch rows whose JP page view repeats an already translated entry (the Zodiac statue scenes
and town hints recur many times in the master script).

    python -X utf8 tools/tl_reuse.py todo b017     # lists the rows still to translate (id, speaker, JP)
    python -X utf8 tools/tl_reuse.py fill b017     # work/tl/b017.new.tsv (your rows) + reused rows -> b017.out.tsv

`fill` copies the English verbatim from script/ (`pages` for master entries), never rewrites it; it fails if a row
is neither reused nor in the .new.tsv file. Then run `tools/batches.py check b017` as usual.
"""
import sys

import batches


def reuse_map():
    found = {}
    for e in batches.index().values():
        en = batches.authored(e)
        if en and e.get("kind", "text") == "text":
            found.setdefault(batches.jp_column(e), en)
    return found


def rows(batch):
    return batches.read_tsv(batches.TL / f"{batch}.tsv")


def main(argv):
    if len(argv) != 2 or argv[0] not in ("todo", "fill"):
        print(__doc__)
        return 2
    cmd, batch = argv
    known = reuse_map()
    if cmd == "todo":
        todo = [r for r in rows(batch) if r[4] not in known]
        for r in todo:
            print("\t".join((r[0], r[1], r[4])))
        print(f"# {len(todo)} to translate, {len(rows(batch)) - len(todo)} reused", file=sys.stderr)
        return 0
    new_path = batches.TL / f"{batch}.new.tsv"
    new = {r[0]: r[1] for r in batches.read_tsv(new_path)} if new_path.exists() else {}
    out, missing = [], []
    for r in rows(batch):
        en = new.get(r[0]) or known.get(r[4])
        if en is None:
            missing.append(r[0])
        else:
            out.append(f"{r[0]}\t{en}")
    if missing:
        print("missing:", " ".join(missing))
        return 1
    (batches.TL / f"{batch}.out.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{batch}.out.tsv: {len(out)} rows ({len(out) - len(new)} reused)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
