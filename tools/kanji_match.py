"""kanji_match.py: rank candidate kanji for every unidentified font code by glyph shape (a first guess only).

    python -X utf8 tools/kanji_match.py [--top 6] [--out work/re/kanji_cand.tsv] [--check 2AB=消,1F1=去]

For each code used in script/ text with no tbl/jp.tbl entry, compare the game's 8x16 glyph (tools/font_sheet.py)
with every JIS level-1/2 kanji drawn by MS Gothic and squeezed to the same cell, and write
code, uses, top candidates with scores, and two script contexts. Shape matching fails on look-alikes (大/太, 土/士):
the final pick needs the script context (docs/re/text.md §Encoding); write it to tbl/kanji.tsv, then
`python -X utf8 tools/mktbl.py --kanji tbl/kanji.tsv > tbl/jp.tbl` and `build.py --dump --refresh`.

Measured weak (2026-11-22, `--check 2AB=消,1F1=去,275=最`): the true kanji ranked 40, 48 and 1011, because the game's
kanji are hand-drawn into 8x12. Use the candidates as hints only; read zoomed sheets with context for the pick.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from font_sheet import glyph  # noqa: E402

FONT_FILE = "C:/Windows/Fonts/msgothic.ttc"


def kanji_set():
    out = []
    for hi in range(0x88, 0xEB):
        if 0xA0 <= hi < 0xE0:
            continue
        for lo in range(0x40, 0xFD):
            try:
                c = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if len(c) == 1 and 0x4E00 <= ord(c) <= 0x9FFF:
                out.append(c)
    return out


def blur(a):
    p = np.pad(a, 1)
    return sum(p[dy:dy + a.shape[0], dx:dx + a.shape[1]] for dy in range(3) for dx in range(3)) / 9.0


def norm(a):
    a = blur(a) - blur(a).mean()
    n = np.linalg.norm(a)
    return (a / n).ravel() if n else a.ravel()


def game_glyph(rom, code):
    g = np.array(glyph(rom, code), dtype=float)
    g = (g == 3).astype(float)  # colour 2 = background, 1 = shadow, 3 = ink
    return g[3:15]              # kanji sit in rows 3-14: an 8x12 box


def render_set(chars, size=48):
    font = ImageFont.truetype(FONT_FILE, size)
    vecs = []
    for c in chars:
        im = Image.new("L", (size, size), 0)
        ImageDraw.Draw(im).text((0, 0), c, fill=255, font=font)
        im = im.resize((8, 12), Image.BOX)
        vecs.append(norm(np.asarray(im, dtype=float) / 255.0))
    return np.stack(vecs)


def unknown_codes():
    """code -> (uses, [contexts]) for every [hhhh] word in script/ text entries that could be a kanji."""
    sys.path.insert(0, str(ROOT / "tools"))
    from script_text import load
    uses, ctx = collections.Counter(), collections.defaultdict(list)
    for name, es in load().items():
        for e in es:
            if e.get("kind") == "data":
                continue
            t = e["jp"].replace("\n", "/")
            for m in re.finditer(r"\[([0-9A-F]{4})\]", t):
                c = int(m.group(1), 16)
                if 0x0010 <= c < 0x0500 and c not in (0x0400,):
                    uses[c] += 1
                    if len(ctx[c]) < 2:
                        ctx[c].append(t[max(0, m.start() - 24):m.end() + 24])
    return uses, ctx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "work" / "re" / "kanji_cand.tsv"))
    ap.add_argument("--check", help="known code=char pairs: print each one's rank and stop")
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Bounty Sword (Japan).sfc").read_bytes()
    chars = kanji_set()
    mat = render_set(chars)
    if a.check:
        for pair in a.check.split(","):
            code, ch = pair.split("=")
            s = mat @ norm(game_glyph(rom, int(code, 16)))
            order = np.argsort(-s)
            rank = [chars[i] for i in order].index(ch) + 1
            print(code, ch, "rank", rank, "top", "".join(chars[i] for i in order[:8]))
        return
    uses, ctx = unknown_codes()
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("code\tuses\tcandidates\tcontext\n")
        for code in sorted(uses):
            s = mat @ norm(game_glyph(rom, code))
            order = np.argsort(-s)[:a.top]
            cand = " ".join(f"{chars[i]}{s[i]:.2f}" for i in order)
            f.write(f"{code:04X}\t{uses[code]}\t{cand}\t{' || '.join(ctx[code])}\n")
    print(f"{len(uses)} codes -> {a.out}")


if __name__ == "__main__":
    main()
