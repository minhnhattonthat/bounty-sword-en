"""The English build as a test: the pre-commit check runs the ROM-level gates of build.py (fixed-field overflow,
asar assemble, romdiff over the allowed ranges + write log, header checksum), not only the text lint."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402

pytestmark = [pytest.mark.skipif(not build.ORIG.exists(), reason="no ROM in this clone"),
              pytest.mark.skipif(not build.ASAR.exists(), reason="tools/asar/asar.exe missing (asar 1.91, gitignored)")]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("build") / "en.sfc"
    try:
        rom, data = build.build(out=out)
    except SystemExit as e:         # overflow, asar or romdiff failure: build.py exits with the reason
        pytest.fail(f"build.py failed: {e}")
    return rom, data, out


def test_english_build_passes_its_rom_gates(built):
    rom, data, out = built
    assert len(data) == 4 * 1024 * 1024
    assert out.read_bytes() == data


def test_default_names_are_english(built):
    _, data, _ = built
    assert data[0x1068D:0x10697] == b"".join((0x0F00 + ord(c)).to_bytes(2, "little") for c in "Sword")
    assert data[0x10657:0x10663] == b"".join((0x0F00 + ord(c)).to_bytes(2, "little") for c in "Thetis")


def test_shop_tilemaps_point_at_the_english_cells(built):
    """script/byte_patches.tsv: each shop map shows whole English words of glyph set 01D2B7 (Arms = tiles C0-C2, at
    the JP header's own column so "Arms 1" stays centred: docs/inkbox.tsv shop_header)."""
    from rom_check import byte_patches
    _, data, _ = built
    patches = byte_patches()
    assert patches, "script/byte_patches.tsv is empty"
    for off, _, new, note in patches:
        assert data[off:off + len(new)] == new, note
    assert data[0x05B230:0x05B237] == bytes.fromhex("4090000302c000")
    assert data[0x32787:0x32791] == b"".join((0x0F00 + ord(c)).to_bytes(2, "little") for c in "Vault")


def test_town_menu_records_are_rewritten(built):
    """Town command menu (C3:966D reads 5-word records at $C3:96B2 + 10 * index): no record keeps its JP bytes."""
    orig, data, _ = built
    for rec in range(0x0396BC, 0x03970C, 10):
        assert data[rec:rec + 10] != orig[rec:rec + 10], f"town menu record {rec:06X} still Japanese"


def test_byte_scripts_reach_their_english(built):
    """tools/byte_scripts.py: every caller of a translated entry points at its English, and the tavern 'Got it!'
    script (05E8F8, ends FF03) still runs on into the roster greeting, whose FF26 jump stays in its bank."""
    import byte_scripts as bs
    from script_text import load
    _, data, _ = built
    files = load(build.SCRIPT)
    codec = bs._codec()
    area = lambda t: any(s <= t < e for s, e in bs.ranges()) or bs.BYTE_AREA[0] <= t < bs.BYTE_AREA[1]
    seen = 0
    for name in bs.BYTE_TABLES:
        for e in files[name + ".json"]:
            if not e.get("en"):
                continue
            head = bs.encode_entry(e["en"], codec).data[:4]
            for r in e.get("refs", ()):
                r = int(r, 16)
                t = (data[r] | data[r + 1] << 8 | data[r + 2] << 16) & 0x3FFFFF
                assert area(t), f"{name} {e['id']}: caller {r:06X} points at {t:06X}"
                assert data[t:t + 4] == head, f"{name} {e['id']}: caller {r:06X} doesn't reach the English"
                seen += 1
    assert seen > 150
    r = 0x06CCC2                                  # `2E ptr24` caller of 05E8F8
    t = (data[r] | data[r + 1] << 8 | data[r + 2] << 16) & 0x3FFFFF
    got_it = next(e for e in files["battle_prompts.json"] if e["id"] == "05E8F8")
    n = len(bs.encode_entry(got_it["en"], codec).data)
    toks = bs.tokens(data, t, t + n + 8)          # the script, then the FF26 that opens 05E954
    assert toks[-2][1] == 0xFF03
    after = toks[-1]
    assert after[1] == bs.JUMP, "05E8F8 no longer runs on into the roster greeting"
    dest = bs._target(after[2])
    assert dest >> 16 == t >> 16
    assert data[dest:dest + 6] == bs.encode_entry('"No', codec).data


def test_part_cards_and_gender_glyph_are_english(built):
    """tools/card_gfx.py draws the 3 part cards into the original 93 tiles + 3 maps; the status gender is ♂/♀."""
    from card_gfx import MAPS_AT, MAP_BYTES, N_TILES, TILES_AT, render
    _, data, _ = built
    tiles, maps = render()
    assert len(tiles) == N_TILES * 16 and tiles[:16] == bytes(16)          # tile 0 = the maps' blank filler
    assert data[TILES_AT:TILES_AT + len(tiles)] == tiles
    for i, m in enumerate(maps):
        words = [int.from_bytes(m[j:j + 2], "little") for j in range(0, MAP_BYTES, 2)]
        assert max(words) < N_TILES and any(words[:64]) and any(words[96:]), f"card {i + 1}: both lines drawn"
        assert data[MAPS_AT + i * MAP_BYTES:MAPS_AT + (i + 1) * MAP_BYTES] == m
    assert data[0x18AA8:0x18AB0] == bytes.fromhex("a94a008003a94900")


def test_strings_tsv_keys_are_where_each_string_starts(built):
    """build.py's strings.tsv (textcover keys): one row per master message and side-table text entry, each address
    in this ROM where that string's bytes start: relocated engine A scripts at their copy, byte tables in bank $FE,
    trampolined engine B entries at their slot (the FF0B jump), the rest in place."""
    import byte_scripts as bs
    from script_text import C1_TABLES, codec_for, load, side_codecs, side_words, ENGINE_B_TABLES
    _, data, out = built
    keys = dict(line.split("\t") for line in out.with_suffix(".strings.tsv").read_text(encoding="utf-8").splitlines())
    files, sc = load(build.SCRIPT), side_codecs()
    masters = sum(1 for f, es in files.items() if f.startswith("master_") for e in es if e.get("slots"))
    sides = [(f[:-5], e) for f, es in files.items() if not f.startswith("master_") for e in es if e.get("kind") == "text"]
    assert len(keys) == masters + len(sides)
    checked = 0
    for name, e in sides:
        at = int(keys[e["id"]], 16) & 0x3FFFFF
        if name in bs.BYTE_TABLES:
            head = bs.encode_entry(e.get("en") or e["jp"], bs._codec()).data[:4]
        else:
            try:
                w = side_words(dict(e, jp=e.get("en") or e["jp"]), codec_for(sc, name), pack=name in C1_TABLES)[:2]
            except ValueError:      # longer than its field as plain text: a tag-font field (below)
                w = [0xFFFF]
            head = b"".join(x.to_bytes(2, "little") for x in w)
        if data[at:at + len(head)] == head:
            checked += 1
        elif name in ENGINE_B_TABLES:
            assert data[at:at + 2] == b"\x0b\xff", f"{name} {e['id']}: neither its text nor a trampoline at {at:06X}"
        else:   # speaker tags and location labels are drawn as tag-font codes, not the plain text
            assert name in ("speakers", "locations", "unit_records"), f"{name} {e['id']}: {at:06X} isn't its text"
    assert checked > 850


def test_battle_setup_name_overrides_are_english(built):
    """tools/re/battle_setup.py: every name override the parser C0:A3AE copies to $1132 (record table C4:2A39) is
    English in the build except the {FF31} variable ones, and the English bytes keep the records parsing the same."""
    sys.path.insert(0, str(ROOT / "tools" / "re"))
    import battle_setup as bsu
    rom, data, _ = built
    fields = bsu.name_fields(rom)
    assert len(fields) > 200
    assert bsu.name_fields(data) == fields
    for off in fields:
        if rom[off:off + 2] == b"\x31\xff":         # {FF31}: the escorted girl's name variable
            assert data[off:off + 12] == rom[off:off + 12]
            continue
        ascii_ = lambda b: 0x20 <= b < 0x7F
        pairs = [(data[off + k], data[off + k + 1]) for k in range(0, 12, 2)]
        english = all(p == (0, 0) or hi == 0x0F and ascii_(lo) or ascii_(lo) and ascii_(hi) for p in pairs
                      for lo, hi in [p])          # $0F00+ASCII, or two letters packed in one word
        assert english and data[off:off + 12] != rom[off:off + 12], f"name override {off:06X} still JP"


def test_header_checksum_is_valid(built):
    _, data, _ = built
    total = sum(data[:0xFFDC]) + sum(data[0xFFE0:]) + 0xFF * 2 & 0xFFFF
    check = int.from_bytes(data[0xFFDE:0xFFE0], "little")
    comp = int.from_bytes(data[0xFFDC:0xFFDE], "little")
    assert check == total and comp == check ^ 0xFFFF
