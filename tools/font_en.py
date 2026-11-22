"""font_en.py: the English font (tools/font_en.txt) as engine data and as widths for the wrap/lint tools.

    from font_en import load, glyph_bytes, advance, text_px
    python -X utf8 tools/font_en.py OUTDIR     -> OUTDIR/font_en.bin (95 glyphs x 32 bytes), font_en_w.bin (95 advances)

Codes: character c (printable ASCII 0x20-0x7E) is the word EN_BASE + ord(c) in the script (tools/script_text.py).
Glyph layout matches the game's font (docs/re/text.md §Font): 2bpp, an 8x16 cell as a top 8x8 tile (16 bytes, rows
0-7) then the bottom tile (rows 8-15); background = colour 2 (plane0 0, plane1 1), ink = colour 3. So plane 1 is
always FF and plane 0 is the ink mask.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "font_en.txt"
EN_BASE = 0x0F00
FIRST, LAST = 0x20, 0x7E
TOP_ROW = 5          # font_en.txt row 0 lands on cell row 5
# Characters the script syntax reserves ({} control words, [] raw words); the font still has them.
RESERVED = set("{}[]")


def load(path=SRC):
    """{char: (rows, advance)}; rows = list of '#'/'.' strings padded to the glyph width."""
    glyphs, cur, rows, adv = {}, None, [], None

    def close():
        if cur is None:
            return
        w = max((len(r) for r in rows), default=0)
        if w > 8 or len(rows) > 16 - TOP_ROW:
            raise ValueError(f"glyph {cur!r}: {w}x{len(rows)} does not fit the 8x{16 - TOP_ROW} area")
        glyphs[cur] = ([r.ljust(w, ".") for r in rows], adv if adv is not None else w + 1)

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and cur is None or not line.strip():
            continue
        if line.startswith("= "):
            close()
            name = line[2:]
            cur, rows, adv = (" " if name == "space" else name), [], None
        elif line.startswith("w "):
            adv = int(line[2:])
        else:
            rows.append(line)
    close()
    missing = [chr(c) for c in range(FIRST, LAST + 1) if chr(c) not in glyphs]
    if missing:
        raise ValueError("font_en.txt lacks " + "".join(missing))
    return glyphs


def glyph_bytes(rows):
    out = bytearray()
    cell = [0] * 16
    for i, r in enumerate(rows):
        cell[TOP_ROW + i] = sum(0x80 >> x for x, ch in enumerate(r) if ch == "#")
    for y in range(16):
        out += bytes((cell[y], 0xFF))
    return bytes(out)          # rows 0-7 = top tile, rows 8-15 = bottom tile


def advance(glyphs=None):
    glyphs = glyphs or load()
    return {c: a for c, (_, a) in glyphs.items()}


def text_px(text, adv=None):
    adv = adv or advance()
    return sum(adv.get(c, 8) for c in text)


def font_block(glyphs=None):
    """Codes EN_BASE+0x20..EN_BASE+0x7F in the game's own font layout (rows of 16 glyphs: 16 top tiles, then the 16
    bottom tiles 0x100 later; 0x200 per row). asm/vwf.asm puts it at $FF:E400, where any glyph address computed the
    game's way, ((c & FFF0) << 5) + ((c & F) << 4) in 16 bits, lands on it with base $FF:0000."""
    glyphs = glyphs or load()
    out = bytearray(0xC00)
    for c in range(FIRST, LAST + 1):
        g = glyph_bytes(glyphs[chr(c)][0])
        k = c - FIRST
        o = (k >> 4) * 0x200 + (k & 15) * 16
        out[o:o + 16] = g[:16]
        out[o + 0x100:o + 0x110] = g[16:]
    for k in range(LAST - FIRST + 1, 0x60):       # code EN_BASE+0x7F: blank background
        o = (k >> 4) * 0x200 + (k & 15) * 16
        out[o:o + 16] = out[o + 0x100:o + 0x110] = bytes((0, 0xFF)) * 8
    return bytes(out)


def build_bin(glyphs=None):
    """font block, then one advance byte per code EN_BASE+0x20..+0x7E."""
    glyphs = glyphs or load()
    widths = bytes(glyphs[chr(c)][1] for c in range(FIRST, LAST + 1))
    if max(widths) > 8:
        raise ValueError("an advance above 8 px breaks the 2-cell renderer")
    return font_block(glyphs) + widths


def write_bins(outdir):
    """outdir/font_en.bin (glyphs) and outdir/font_en_w.bin (advances), the files asm/vwf.asm incbins."""
    b = build_bin()
    Path(outdir, "font_en.bin").write_bytes(b[:0xC00])
    Path(outdir, "font_en_w.bin").write_bytes(b[0xC00:])


if __name__ == "__main__":
    write_bins(sys.argv[1])
