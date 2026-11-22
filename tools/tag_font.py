"""tag_font.py: English speaker name tags and location labels, pre-rendered proportionally at build time (D8).

The name tag (6 cells, C2:5641 path) and the location label (10 cells, C0:E1B1) draw one 8x16 glyph per word, with
no VWF. Instead of packing letters at run time, the build renders each English string with the English font
(tools/font_en.py advances) into its cells and gives every distinct cell bitmap a code of its own from TAG_FIRST up.
The tiles sit in the game's font layout at $FF:A000, where the game's glyph-offset formula puts those codes with
base $FF:0000 (asm/vwf.asm NameGlyph/CardGlyph switch to that base for offsets >= $A000). Codes 0x0500-0x071F are
free and land there: JP glyph words end at 0x04FC. A fully blank cell uses the JP space word (0000), like the JP
padding. Location labels are centred to whole cells so they share cells.

    from tag_font import TagFont, speaker_names
    tf = TagFont(); words = tf.words("Tsukikage", 6); tf.write(BUILD / "font_tag.bin")

`script/speaker_tags.tsv` (jp name<TAB>English) names every speaker: the speakers table and the `{spk}` headers of
master text render from it, so a header and its table row get the same codes (the game matches them for the
portrait).
"""
import re
from pathlib import Path

from font_en import TOP_ROW, load

ROOT = Path(__file__).resolve().parents[1]
NAMES = ROOT / "script" / "speaker_tags.tsv"
# [first, end): offsets $A000..$E3F0, below the English font at $E400. The formula truncates to 16 bits, so codes
# from 0x0720 on wrap to offsets below $A000 (which the hooks read as JP): 544 codes in all.
TAG_FIRST, TAG_END = 0x0500, 0x0720
BLOCK_BASE = 0xA000
TAG_CELLS = {"speakers": 6, "locations": 10}
CENTRED = {"locations"}                  # the JP centred location labels with spaces; speaker names are left-aligned
SPACE = 0x0000
HEADER = re.compile(r"\{spk\}([^\n{\[]{6})")   # a literal 6-word speaker header (variable headers start with "{")


def offset(code):
    return (((code & 0xFFF0) << 5) + ((code & 0xF) << 4)) & 0xFFFF


def speaker_names(path=NAMES):
    out = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            jp, en = line.split("\t")
            out[jp] = en
    return out


class TagFont:
    def __init__(self):
        self.glyphs = load()
        self.codes = {}          # cell bitmap (32 bytes) -> code

    def px(self, text):
        return sum(self.glyphs[c][1] for c in text)

    def fits(self, text, cells):
        """The last glyph's advance column is blank, so one pixel may pass the field edge."""
        return self.px(text) - 1 <= cells * 8

    def render(self, text, cells, centre=False):
        """16 rows of cells*8 ink flags."""
        if not self.fits(text, cells):
            raise ValueError(f"{text!r}: {self.px(text)} px, the field is {cells * 8} px")
        width = cells * 8
        # centred to whole cells: pixel centring would give each label its own cells and fill the tag font
        x = (width - (self.px(text) - 1)) // 2 // 8 * 8 if centre else 0
        rows = [[0] * (width + 8) for _ in range(16)]
        for c in text:
            g, adv = self.glyphs[c]
            for y, r in enumerate(g):
                for dx, ch in enumerate(r):
                    if ch == "#":
                        rows[TOP_ROW + y][x + dx] = 1
            x += adv
        return [r[:width] for r in rows]

    def words(self, text, cells, centre=False):
        rows = self.render(text, cells, centre)
        out = []
        for k in range(cells):
            cell = bytearray()
            for y in range(16):
                cell += bytes((sum(0x80 >> i for i in range(8) if rows[y][k * 8 + i]), 0xFF))
            cell = bytes(cell)
            if not any(cell[0::2]):
                out.append(SPACE)
                continue
            if cell not in self.codes:
                code = TAG_FIRST + len(self.codes)
                if code >= TAG_END:
                    raise ValueError("tag font full: more than %d distinct cells" % (TAG_END - TAG_FIRST))
                self.codes[cell] = code
            out.append(self.codes[cell])
        return out

    def script(self, text, cells, centre=False):
        """The words as script syntax `[hhhh]...`."""
        return "".join("[%04X]" % w for w in self.words(text, cells, centre))

    def block(self):
        """Tiles for every used code, laid out from $FF:A000 (top tile at offset(code), bottom tile 0x100 later)."""
        if not self.codes:
            return b""
        end = max(offset(c) for c in self.codes.values()) + 0x110 - BLOCK_BASE
        out = bytearray(b"\xff" * end)
        for cell, code in self.codes.items():
            o = offset(code) - BLOCK_BASE
            out[o:o + 16] = cell[:16]
            out[o + 0x100:o + 0x110] = cell[16:]
        return bytes(out)

    def write(self, path):
        Path(path).write_bytes(self.block() or b"\xff")


def headers(text, names, tf):
    """Master text: every literal `{spk}` header -> its English tag codes. Unknown names raise."""
    def sub(m):
        jp = m.group(1).rstrip("　")
        if jp not in names:
            raise ValueError(f"speaker {jp!r} has no row in {NAMES.name}")
        return "{spk}" + tf.script(names[jp], 6)
    return HEADER.sub(sub, text)
