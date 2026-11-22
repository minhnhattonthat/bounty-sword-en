"""Phase 4 extract: every string roundtrips through script/ and the entries cover every text range."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rom_text import REGIONS, WordCodec, read_slots, repack, unpack, words_at  # noqa: E402
from script_text import (ENGINE_B_TABLES, SCRIPT, TextCodec, apply_script, dump, extract, load,  # noqa: E402
                         side_codecs, side_words)

ROM = ROOT / "rom" / "Bounty Sword (Japan).sfc"


@pytest.fixture(scope="module")
def rom():
    if not ROM.exists():
        pytest.skip("original ROM not present")
    return ROM.read_bytes()


@pytest.fixture(scope="module")
def files(rom):
    return extract(rom)


@pytest.fixture(scope="module")
def layout(rom):
    return unpack(rom)


def test_whole_rom_roundtrip_through_jp(rom, files):
    assert repack(rom, apply_script(rom, files)) == rom


def test_every_master_string_roundtrips(rom, files, layout):
    mc, wc = TextCodec(True), WordCodec()
    n = 0
    for blk in layout["master"]["blocks"]:
        entries = files["master_%06X.json" % blk["start"]]
        for e, raw in zip(entries, blk["msgs"], strict=True):
            assert mc.encode(e["jp"]) == wc.encode(raw), e["id"]
            n += 1
    assert n == 2335


def test_every_side_string_roundtrips(rom, files):
    sc = side_codecs()
    for name, start, end in REGIONS:
        for e in files[name + ".json"]:
            w = side_words(e, sc[name in ENGINE_B_TABLES])
            off = int(e["id"], 16)
            assert w == words_at(rom, off, off + 2 * len(w)), (name, e["id"])


def test_master_entries_tile_blocks(rom, files, layout):
    mc = TextCodec(True)
    for blk in layout["master"]["blocks"]:
        p = blk["start"]
        for e in files["master_%06X.json" % blk["start"]]:
            assert int(e["id"], 16) == p, f"gap or overlap before {e['id']}"
            p += 2 * len(mc.encode(e["jp"]))
        assert p == blk["end"]


def test_master_slots_all_reach_an_entry(rom, files):
    slots = read_slots(rom)
    owner = {i: e["id"] for es in files.values() for e in es for i in e.get("slots", [])}
    for i, v in enumerate(slots):
        if v:
            assert owner[i] == "%06X" % (v & 0x3FFFFF), i
        else:
            assert i not in owner


def test_side_entries_tile_regions(files):
    sc = side_codecs()
    for name, start, end in REGIONS:
        p = start
        for e in files[name + ".json"]:
            assert int(e["id"], 16) == p, f"{name}: gap or overlap before {e['id']}"
            p += 2 * len(side_words(e, sc[name in ENGINE_B_TABLES]))
        assert p == end, name


def test_text_entries_have_en_and_data_has_none(files):
    for name, es in files.items():
        for e in es:
            if e.get("kind") == "data":
                assert "en" not in e, e["id"]
            else:
                assert e.get("en") == "", e["id"]


def test_codec_tokens():
    mc = TextCodec(True)
    w = [0xFF15, 0xFF28, 0xFFFF, 0x36, 0, *range(0xFF19, 0xFF1F), 0x37, 0xFFFF, 0xFF18, 0xFF14, 3, 0x400, 1, 0xFF00]
    t = mc.decode(w)
    assert t == "{spk}{FF28}\n「　{hero}」\n{next}{FF14:0003}‥[0001]{end}"
    assert mc.encode(t) == w
    with pytest.raises(ValueError):
        mc.encode("{0041}")
    with pytest.raises(ValueError):
        mc.decode([0xFF2D, 0, 0, 0, 0])


def test_script_files_are_current(files):
    """script/ jp fields equal a fresh extract (re-run build.py --dump --refresh after a table change)."""
    on_disk = load(SCRIPT)
    assert set(on_disk) == set(files)
    for name, es in files.items():
        assert [(e["id"], e["jp"]) for e in es] == [(e["id"], e["jp"]) for e in on_disk[name]], name


def test_dump_never_clobbers_english(rom, tmp_path):
    written, _ = dump(rom, out=tmp_path)
    assert written
    p = tmp_path / "locations.json"
    es = json.loads(p.read_text(encoding="utf-8"))
    i = next(k for k, e in enumerate(es) if e.get("kind") == "text")
    es[i]["en"] = "Rheinmetall"
    p.write_text(json.dumps(es, ensure_ascii=False), encoding="utf-8")
    assert dump(rom, out=tmp_path)[0] == []
    dump(rom, out=tmp_path, refresh=True)
    assert json.loads(p.read_text(encoding="utf-8"))[i]["en"] == "Rheinmetall"


def test_english_moves_master_pointers(rom, files):
    f = copy.deepcopy(files)
    e = f["master_1E0000.json"][3]
    e["en"] = e["jp"] + "ア"
    last = f["master_1E0000.json"][-1]           # make room: drop the last message's final word
    last["en"] = last["jp"][:-1]
    out = repack(rom, apply_script(rom, f, field="en"))
    slots = read_slots(out)
    nxt = f["master_1E0000.json"][4]
    assert slots[nxt["slots"][0]] & 0x3FFFFF == int(nxt["id"], 16) + 2
