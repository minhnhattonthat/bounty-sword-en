"""story_chapters.py: chapter files for the phase 9 story pass (`>> id | <speaker> JP` / `EN`, ROM order).

    python -X utf8 tools/story_chapters.py [--out work/qa/story/chapters] [--size 150]

No scene-to-chapter map exists (docs/synopsis.md has no chapter list), so a "chapter" is one master script file in
ROM order (the game stores its dialogue roughly in story order), split into parts of about --size entries at a
point where the speaker changes. Every master entry lands in exactly one file. Then:

    python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402
import pairs  # noqa: E402


def chapters(size):
    """Yield (name, [entry, ...]) for every master script file, split into parts of about `size` entries."""
    for path, _, doc in batches.docs():
        if not path.stem.startswith("master_"):
            continue
        n = max(1, round(len(doc) / size))
        step = -(-len(doc) // n)
        for k in range(n):
            part = doc[k * step:(k + 1) * step]
            if part:
                yield f"{path.stem}_{k + 1}of{n}", part


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="work/qa/story/chapters")
    ap.add_argument("--size", type=int, default=150)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, (name, part) in enumerate(chapters(a.size), 1):
        f = out / f"c{i:02d}_{name}.txt"
        f.write_text("\n".join(pairs.row(e, ">>") for e in part) + "\n", encoding="utf-8")
        total += len(part)
        print(f"{f}\t{len(part)}")
    print(f"{total} entries")


if __name__ == "__main__":
    main()
