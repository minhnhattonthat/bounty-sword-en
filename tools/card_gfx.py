"""card_gfx.py: the part cards (第1部『迫り来る恐怖』..) redrawn in English with the project font.

    from card_gfx import patches       -> [(offset, original bytes, new bytes, note)] for the build
    python -X utf8 tools/card_gfx.py [OUT.png]   -> preview of the three cards, prints the tile count

The card is BG3 (2bpp): loader table C1:514C.. entry `9A 44 D8 | 00 40 | D0 05 | D0 05` copies 93 tiles
($5D0 bytes at $D8:449A = file 0x18449A) to VRAM $8000; the next three entries copy one tilemap each ($140 bytes =
5 rows of 32 words, at $D8:4A6A / $D8:4BAA / $D8:4CEA) to VRAM $8800 (word $4400). Rows 0-1 hold 第N部, rows 3-4
the title. Colour 0 = transparent, 3 = white (1 = grey, unused here). Tile 0 must stay blank (the maps' filler).
The English cards are drawn into the same 93 tiles and the same three maps, so nothing moves.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font_en import TOP_ROW, load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TILES_AT, N_TILES = 0x18449A, 0x5D
MAPS_AT, MAP_BYTES = 0x184A6A, 0x140
CARDS = [("Part 1", "Terror Draws Near"),
         ("Part 2", "In a Faraway Land"),
         ("Part 3", "Into the Heart of Evil")]
LINE_ROWS = (0, 3)          # tile row of each line's top half
INK = 3


def line_bitmap(text, glyphs):
    """16 rows x 256 px of colour indices, the text centred (pixel precise) in the 256 px line."""
    width = sum(glyphs[c][1] for c in text) - 1
    x = (256 - width) // 2
    rows = [[0] * 256 for _ in range(16)]
    for c in text:
        pix, adv = glyphs[c]
        for y, r in enumerate(pix):
            for dx, ch in enumerate(r):
                if ch == "#":
                    rows[TOP_ROW + y][x + dx] = INK
        x += adv
    return rows


def tile_bytes(rows, tx, ty):
    """8x8 2bpp tile at tile column tx, tile row ty (0/1) of a 16-row line bitmap."""
    out = bytearray()
    for y in range(8):
        p0 = p1 = 0
        for x in range(8):
            v = rows[ty * 8 + y][tx * 8 + x]
            p0 |= (v & 1) << (7 - x)
            p1 |= (v >> 1) << (7 - x)
        out += bytes((p0, p1))
    return bytes(out)


def render():
    """(tile data bytes, [map bytes per card]); raises if the cards need more than the original 93 tiles."""
    glyphs = load()
    tiles = [bytes(16)]                       # tile 0 = blank
    index = {tiles[0]: 0}
    maps = []
    for card in CARDS:
        words = [0] * (5 * 32)
        for text, row0 in zip(card, LINE_ROWS):
            bm = line_bitmap(text, glyphs)
            for ty in range(2):
                for tx in range(32):
                    t = tile_bytes(bm, tx, ty)
                    if t not in index:
                        index[t] = len(tiles)
                        tiles.append(t)
                    words[(row0 + ty) * 32 + tx] = index[t]
        maps.append(b"".join(w.to_bytes(2, "little") for w in words))
    if len(tiles) > N_TILES:
        raise ValueError(f"part cards need {len(tiles)} tiles, the loader copies {N_TILES}")
    data = b"".join(tiles).ljust(N_TILES * 16, b"\0")
    return data, maps


def patches(rom_path=None):
    """[(offset, original, new, note)]: the tile block and the three maps (originals read from the dump)."""
    orig = Path(rom_path or ROOT / "rom" / "Bounty Sword (Japan).sfc").read_bytes()
    data, maps = render()
    out = [(TILES_AT, orig[TILES_AT:TILES_AT + len(data)], data, "part card tiles (tools/card_gfx.py)")]
    for i, m in enumerate(maps):
        o = MAPS_AT + i * MAP_BYTES
        out.append((o, orig[o:o + MAP_BYTES], m, f"part card {i + 1} tilemap (tools/card_gfx.py)"))
    return out


def preview(out):
    from PIL import Image
    data, maps = render()
    img = Image.new("RGB", (256, 3 * 48), (0, 0, 0))
    pal = [(0, 0, 0), (82, 82, 82), (0, 0, 0), (247, 247, 231)]
    for n, m in enumerate(maps):
        for i in range(5 * 32):
            t = int.from_bytes(m[2 * i:2 * i + 2], "little")
            tb = data[t * 16:t * 16 + 16]
            for y in range(8):
                for x in range(8):
                    v = ((tb[2 * y] >> (7 - x)) & 1) | (((tb[2 * y + 1] >> (7 - x)) & 1) << 1)
                    img.putpixel(((i % 32) * 8 + x, n * 48 + (i // 32) * 8 + y), pal[v])
    img.save(out)


if __name__ == "__main__":
    data, _ = render()
    print(f"{len(data.rstrip(bytes(1))) // 16 + 1} tiles used of {N_TILES}")
    if len(sys.argv) > 1:
        preview(sys.argv[1])
