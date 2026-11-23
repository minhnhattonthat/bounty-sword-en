"""grid.py: lay out English in C1 grid strings (menus, windows, menus_c) cell by cell.

A grid string is drawn into tile slots 0..n-1 (one slot = one 8-px cell) and the screen's tilemaps show slices of
those slots (docs/re/vwf.md width gate, docs/re/slices.tsv). C1Run (asm/vwf.asm) draws English proportionally (VWF
mode 2) from cell 0, the whole field cleared first. Two cursor codes:
  `[0F7F]` TAB   PX = ceil((PX - 1) / 8) * 8: the first cell edge after the ink (a glyph's last column is blank
                 spacing and may spill 1 px into the next cell); at an edge it stays put.
  `[0F1F][00nn]` SETX: PX = nn * 8, jump to cell nn (two words, any distance).
Two ASCII letters share a word (script_text.pack_pairs) and the string keeps its JP word count. Non-ASCII
characters (JP glyphs, full-width letters) are 8 px, one cell each.

Author a grid string as `cell:text` items joined by ` | ` (cells counted from 0, the JP word's first cell):

    python -X utf8 tools/grid.py layout 29 "1:Party | 5:Tac | 7:Itm"     -> script syntax with cursor codes
    python -X utf8 tools/grid.py show "Party[0F7F]Itm" 29                  -> each run's cells and pixels
    python -X utf8 tools/grid.py fill b057 work/tl/grid_specs.tsv          -> work/tl/b057.out.tsv (`=` keeps the JP)

An item's text must end by the next item's cell (+1 px spill), or by `cell+cells` when given (`7+2:Itm`).
`problems(en, width)` (batches.py check) re-checks any grid string: packed words and the last cell.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font_en import text_px  # noqa: E402

TAB, SETX = "[0F7F]", "[0F1F]"
CURSOR = re.compile(r"\[0F7F\]|\[0F1F\]\[[0-9A-F]{4}\]")
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]")
SPILL = 1
GRID_FILES = {"menus", "windows", "menus_c"}


def tab(px):
    return (px + 6) // 8 * 8


def px_of(text):
    """Pixels of text with no cursor codes: ASCII by the English font, other chars and codes 8 px each."""
    px = 0
    for tok in re.split(f"({TOKEN.pattern})", text):
        if tok:
            px += 8 if TOKEN.fullmatch(tok) else sum(text_px(c) if " " <= c <= "~" else 8 for c in tok)
    return px


def runs(en):
    """(start px, end px, text) for each run between cursor codes."""
    out, px, pos = [], 0, 0
    for m in list(CURSOR.finditer(en)) + [None]:
        text = en[pos:m.start() if m else len(en)]
        out.append((px, px + px_of(text), text))
        px += px_of(text)
        if m:
            px = tab(px) if m.group() == TAB else int(m.group()[-5:-1], 16) * 8
            pos = m.end()
    return out


def words(en):
    """Packed word count: each pair of consecutive ASCII chars is one word, anything else one word."""
    n, run = 0, 0
    for tok in re.split(f"({TOKEN.pattern})", en):
        for piece in ([tok] if TOKEN.fullmatch(tok or "x") else list(tok)):
            if len(piece) == 1 and " " <= piece <= "~":
                run += 1
                continue
            n += (run + 1) // 2 + 1
            run = 0
    return n + (run + 1) // 2


def problems(en, width):
    out = []
    if (n := words(en)) > width:
        out.append(f"{n} words packed, string holds {width}")
    for start, end, text in runs(en):
        if end > width * 8 + SPILL:
            out.append(f"'{text}' ends at {end} px, past cell {width}")
    return out


LATE = 3   # cheap mode: an item may start up to 3 px into its cell (spaces instead of a TAB)


def move(px, cell, cheap):
    """Cursor codes from px to cell * 8 and the px where the item starts. Exact: nothing, one TAB, or SETX.
    Cheap: also run straight on after a 1-px spill, or pad with 4-px spaces (they pack two a word)."""
    t = cell * 8
    if px == t:
        return "", px
    if cheap and t < px <= t + SPILL:
        return "", px
    if tab(px) == t:
        return TAB, t
    if cheap and px < t:
        n = -(-(t - px) // 4)
        if px + 4 * n <= t + LATE and n <= 3:
            return " " * n, px + 4 * n
    return f"{SETX}[{cell:04X}]", t


def layout(width, spec):
    items = []
    for item in spec.split(" | "):
        m = re.fullmatch(r"\s*(\d+)(?:\+(\d+))?:(.*)", item, re.S)
        if not m:
            raise ValueError(f"bad item {item!r} (want cell:text or cell+cells:text)")
        items.append((int(m.group(1)), int(m.group(2)) if m.group(2) else None, m.group(3)))
    for cheap in (False, True):
        en, px = "", 0
        for k, (cell, cells, text) in enumerate(items):
            if px > cell * 8 + (SPILL if k else 0):
                raise ValueError(f"cell {cell}: the text before ends at {px} px")
            end_cell = cell + cells if cells else (items[k + 1][0] if k + 1 < len(items) else width)
            w = px_of(text)
            codes, start = move(px, cell, cheap)
            if start + w > end_cell * 8 + SPILL:          # a late start doesn't fit: start exactly
                codes, start = move(px, cell, False)
            en += codes
            px = start
            if px + w > end_cell * 8 + SPILL:
                raise ValueError(f"cell {cell}: '{text}' is {w} px from {px - cell * 8} px in, "
                                 f"room {end_cell * 8 + SPILL - cell * 8} px")
            en += text
            px += w
        if not problems(en, width):
            return en
    raise ValueError("; ".join(problems(en, width)))


def fill(batch, specs_path):
    """work/tl/<batch>.out.tsv from a specs TSV (id<TAB>cell:text | ... ; `=` keeps the JP): every id of the batch
    must have a spec. Prints each id's problem and writes nothing if any."""
    import json
    root = Path(__file__).resolve().parents[1]
    entries = {}
    for f in sorted(GRID_FILES):
        for e in json.loads((root / f"script/{f}.json").read_text(encoding="utf-8")):
            entries[e["id"]] = e
    specs = dict(line.rstrip("\n").split("\t", 1) for line in open(specs_path, encoding="utf-8") if line.strip())
    out, bad = [], []
    for line in open(root / f"work/tl/{batch}.tsv", encoding="utf-8"):
        eid = line.split("\t", 1)[0]
        e, spec = entries[eid], specs.get(eid)
        try:
            if spec is None:
                raise ValueError("no spec")
            out.append(f"{eid}\t{e['jp'] if spec == '=' else layout(e.get('cells') or e['width'], spec)}")
        except ValueError as err:
            bad.append(f"{eid}: {err}")
    print(*bad, sep="\n")
    if not bad:
        (root / f"work/tl/{batch}.out.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"{batch}: {len(out)} rows written")
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ["fill"] and len(argv) == 3:
        return fill(argv[1], argv[2])
    if argv[:1] == ["layout"] and len(argv) == 3:
        print(layout(int(argv[1]), argv[2]))
    elif argv[:1] == ["show"] and len(argv) == 3:
        for start, end, text in runs(argv[1]):
            print(f"cell {start // 8:3d}-{max(start, end - 2) // 8:3d}  {end - start:3d} px  {text}")
        print(f"{words(argv[1])} words / {argv[2]}", *problems(argv[1], int(argv[2])), sep="\n")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
