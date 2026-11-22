"""kanji_align.py: identify the sorted kanji block by aligning glyph shapes with the JIS level-1 order.

    python -X utf8 tools/kanji_align.py [--anchor 220=回,263=古] [--out work/re/kanji_align.tsv]

Font codes 0x200 up are the game's kanji in JIS X 0208 level-1 order (Shift-JIS order; 0x200 = 愛, 0x206 = 一,
0x220 = 回, 0x263 = 古), one glyph each, codes with no glyph skipped. Codes 0x1C8-0x1F8 are an unordered block added
later (去 = 0x1F1) and are not handled here. Shape scores alone are weak (tools/kanji_match.py ranks the true kanji
40th..1000th), but the order constraint leaves ~4 candidates per code: this finds the strictly increasing
assignment code -> kanji with the highest total score (dynamic programming), with --anchor pairs forced.

Output TSV: code, kanji, score, rank of that kanji among the code's own top candidates, gap to the previous pick
(JIS steps), the top 4 free candidates, and a script context. Low score + big gap = check it by eye.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from kanji_match import game_glyph, norm, render_set, unknown_codes  # noqa: E402

FIRST, LAST = 0x200, 0x38B  # 0x38B = 和; 0x38C-0x4FF is another unordered block


def level1():
    out = []
    for hi in range(0x88, 0x99):
        for lo in range(0x40, 0xFD):
            if hi == 0x88 and lo < 0x9F or hi == 0x98 and lo > 0x72:
                continue
            try:
                c = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if len(c) == 1 and 0x4E00 <= ord(c) <= 0x9FFF:
                out.append(c)
    return out


def align(score):
    """score[i, j] -> list of j, strictly increasing, maximising the sum."""
    n, m = score.shape
    best = np.full((n, m), -np.inf)
    back = np.zeros((n, m), dtype=int)
    best[0] = score[0]
    for i in range(1, n):
        prev = best[i - 1]
        run = np.maximum.accumulate(prev)              # run[j] = max(prev[:j+1])
        arg = np.zeros(m, dtype=int)
        cur = 0
        for j in range(m):                            # argmax of prev[:j+1]
            if prev[j] > prev[cur]:
                cur = j
            arg[j] = cur
        best[i, 1:] = score[i, 1:] + run[:-1]
        back[i, 1:] = arg[:-1]
    j = int(np.argmax(best[-1]))
    path = [j]
    for i in range(n - 1, 0, -1):
        j = back[i, j]
        path.append(j)
    return path[::-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anchor", default="", help="code=kanji pairs to force, comma-separated")
    ap.add_argument("--anchors-file", help="TSV code<TAB>kanji to force (e.g. tbl/kanji.tsv)")
    ap.add_argument("--out", default=str(ROOT / "work" / "re" / "kanji_align.tsv"))
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Bounty Sword (Japan).sfc").read_bytes()
    chars = level1()
    index = {c: k for k, c in enumerate(chars)}
    mat = render_set(chars)
    codes, vecs = [], []
    for code in range(FIRST, LAST + 1):
        g = game_glyph(rom, code)
        if g.sum() > 0:
            codes.append(code)
            vecs.append(norm(g))
    score = np.stack(vecs) @ mat.T
    anchors = {}
    for pair in filter(None, a.anchor.split(",")):
        k, v = pair.split("=")
        anchors[int(k, 16)] = v
    if a.anchors_file:
        for line in Path(a.anchors_file).read_text(encoding="utf8").splitlines():
            if line and not line.startswith("#"):
                k, v = line.split("\t")[:2]
                if FIRST <= int(k, 16) <= LAST:
                    anchors[int(k, 16)] = v
    # the game's order is JIS with a few local swaps (大 谷 第): drop anchors that break it, and their codes
    keyed = sorted((c, index[k]) for c, k in anchors.items())
    for (c0, j0), (c1, j1), (c2, j2) in zip(keyed, keyed[1:], keyed[2:]):
        if not (j0 < j1 < j2) and (j0 < j2):
            del anchors[c1]
            keep = [i for i, c in enumerate(codes) if c != c1]
            codes, vecs, score = [codes[i] for i in keep], [vecs[i] for i in keep], score[keep]
    free = score.copy()
    for i, code in enumerate(codes):
        if code in anchors:
            score[i] = -1e3
            score[i, index[anchors[code]]] = 1e3
    path = align(score)
    uses, ctx = unknown_codes()
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("code\tkanji\tscore\trank\tgap\ttop\tcontext\n")
        prev = -1
        for i, (code, j) in enumerate(zip(codes, path)):
            order = list(np.argsort(-free[i]))
            rank = order.index(j) + 1
            top = "".join(chars[k] for k in order[:4])
            mark = "A" if code in anchors else ""
            f.write(f"{code:04X}\t{chars[j]}{mark}\t{free[i, j]:.2f}\t{rank}\t{j - prev}\t{top}\t"
                    f"{' || '.join(ctx.get(code, []))}\n")
            prev = j
    print(f"{len(codes)} codes, last pick {chars[path[-1]]} (JIS index {path[-1]} of {len(chars)}) -> {a.out}")


if __name__ == "__main__":
    main()
