"""English font, encoding and marker build (phase 5; docs/re/vwf.md)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from font_en import EN_BASE, FIRST, LAST, advance, build_bin, load  # noqa: E402
from marker import CLOSE, LINE_PX, TORTURE, master_marker, wrap_px  # noqa: E402
from script_text import SCRIPT, TextCodec, load as load_script  # noqa: E402


def test_font_covers_ascii_and_fits_two_cells():
    glyphs = load()
    assert set(glyphs) == {chr(c) for c in range(FIRST, LAST + 1)}
    for c, (rows, adv) in glyphs.items():
        assert len(rows) <= 11 and all(len(r) <= 8 for r in rows), c
        assert 1 <= adv <= 8, c          # the renderer spills into at most one extra cell
    assert len(build_bin()) == 0xC00 + (LAST - FIRST + 1)


def test_font_block_matches_the_games_glyph_address_formula():
    from font_en import font_block, glyph_bytes
    block, glyphs = font_block(), load()
    for ch in "Ag~":
        c = EN_BASE + ord(ch)
        y = (((c & 0xFFF0) << 5) + ((c & 0xF) << 4)) & 0xFFFF     # what the game's code computes
        o = y - 0xE400                                            # block sits at $FF:E400
        g = glyph_bytes(glyphs[ch][0])
        assert block[o:o + 16] == g[:16] and block[o + 0x100:o + 0x110] == g[16:]


def test_ascii_encodes_to_english_codes():
    codec = TextCodec(True)
    assert codec.encode("Hi!") == [EN_BASE + ord("H"), EN_BASE + ord("i"), EN_BASE + ord("!")]
    assert codec.encode("「A」") == [0x36, EN_BASE + ord("A"), 0x37]


def line_px(line):
    adv = advance()
    text = re.sub(r"\{[^}]*\}", "", line)
    return sum(adv['"'] if c == CLOSE else adv[c] for c in text)


def test_marker_keeps_structure_and_fills_lines_exactly():
    files = load_script(SCRIPT)
    n = 0
    for name, entries in files.items():
        if not name.startswith("master_"):
            continue
        for e in entries:
            m = master_marker(e["id"], e["jp"], torture=False)
            for tok in ("{spk}", "{end}", "{FF2F}", "{FF30}"):
                assert m.count(tok) == e["jp"].count(tok), (e["id"], tok)
            assert m.count("{next}") == e["jp"].count("{next}"), e["id"]
            assert m.count("\n") == e["jp"].count("\n"), e["id"]
            for line in m.split("\n"):
                if line.endswith("|") or line.endswith("|" + CLOSE):
                    assert LINE_PX - 1 <= line_px(line) <= LINE_PX, (e["id"], line)
                    n += 1
    assert n > 5000


def test_torture_line_wraps_inside_the_box():
    assert all(line_px(x) <= LINE_PX for x in wrap_px(TORTURE, LINE_PX - 8))
