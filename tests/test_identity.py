"""Phase 3 identity build: unpack -> repack with no edits gives the original dump; edits move pointers correctly."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM_PATH = ROOT / "rom" / "Bounty Sword (Japan).sfc"

from rom_text import MASTER_BLOCKS, WordCodec, read_slots, repack, to_file, unpack  # noqa: E402

pytestmark = pytest.mark.skipif(not ROM_PATH.exists(), reason="no ROM in this clone")


@pytest.fixture(scope="module")
def rom():
    return ROM_PATH.read_bytes()


@pytest.fixture(scope="module")
def codec():
    return WordCodec()


@pytest.fixture(scope="module")
def data(rom, codec):
    return unpack(rom, codec)


def test_identity(rom, data, codec):
    assert repack(rom, data, codec) == rom


def test_master_shape(data):
    m = data["master"]
    assert len(m["slots"]) == 2462
    assert sum(1 for s in m["slots"] if s) == 2336
    assert sum(len(b["msgs"]) for b in m["blocks"]) == 2335
    assert tuple(b["start"] for b in m["blocks"]) == MASTER_BLOCKS


def test_codec_roundtrip_every_word(codec):
    words = list(range(0x10000))
    assert codec.encode(codec.decode(words)) == words


def test_edit_moves_pointers(rom, data, codec):
    """Grow one message by 2 words and shrink a later one by 2 words in the same block: every slot still points at
    the same message text, and the bytes after the block are untouched."""
    import copy
    d = copy.deepcopy(data)
    blk = d["master"]["blocks"][1]
    blk["msgs"][3] = blk["msgs"][3] + "[0000][0000]"
    last = codec.encode(blk["msgs"][-1])
    blk["msgs"][-1] = codec.decode(last[:-4] + last[-2:])   # drop two words before the final 」FFFF
    out = repack(rom, d, codec)
    assert out != rom
    slots = read_slots(out)
    for i, ref in enumerate(d["master"]["slots"]):
        if ref is None:
            assert slots[i] == 0
            continue
        want = codec.encode_bytes(d["master"]["blocks"][ref[0]]["msgs"][ref[1]])
        o = to_file(slots[i])
        assert out[o:o + len(want)] == want, i
    end = d["master"]["blocks"][1]["end"]
    assert out[end:end + 0x100] == rom[end:end + 0x100]


def test_overflow_moves_to_expanded_rom(rom, data, codec):
    """A message that no longer fits its block goes to the expanded 4 MB area ($F0+), never across a bank."""
    import copy
    from rom_text import EXPANDED_TEXT, MASTER_TABLE, read_slots, to_file
    d = copy.deepcopy(data)
    d["master"]["blocks"][0]["msgs"][0] += "[0000]" * 0x6000     # 48 KB: more than block 0 holds
    out = repack(rom, d, codec)
    assert len(out) == 0x400000
    slot = d["master"]["slots"].index([0, 0])
    target = to_file(read_slots(out)[slot])
    assert EXPANDED_TEXT[0] <= target < EXPANDED_TEXT[1]
    n = len(codec.encode_bytes(d["master"]["blocks"][0]["msgs"][0]))
    assert target >> 16 == (target + n - 1) >> 16
    assert MASTER_TABLE    # table rewritten in place (read_slots read it)
    d["master"]["blocks"][0]["msgs"][1] += "[0000]" * 0x80000
    with pytest.raises(ValueError, match="full"):
        repack(rom, d, codec)


def test_grown_side_script_moves_and_callers_follow(rom, codec):
    """An engine A prompt script (question + choice list, FF03 runs on) that outgrows its slot moves to $F0+ whole;
    its `03 ptr24` caller points at it; the old bytes stay; a shorter one is padded in place; a grown script with
    no known caller is refused."""
    import copy
    from rom_text import EXPANDED_TEXT, to_file
    from script_text import apply_script, load
    files = copy.deepcopy(load())
    for es in files.values():
        for e in es:
            e["en"] = ""
    sp = {e["id"]: e for e in files["system_prompts.json"]}
    sp["04148F"]["en"] = '{FF09:0000}{FF12}"Will you accept the challenge to a duel?"{FF04}{FF03}'
    sp["0414B3"]["en"] = "  Yes{FF11}  No{FF14:0002}{FF00}"
    sp["041449"]["en"] = '{FF12}"Here."{FF04}{FF00}'
    out = repack(rom, apply_script(rom, files, field="en"), codec)
    target = to_file(int.from_bytes(out[0x041296:0x041299], "little"))
    assert EXPANDED_TEXT[0] <= target < EXPANDED_TEXT[1] and out[0x041295] == 0x03
    from script_text import side_codecs, side_words
    a = side_codecs()["A"]
    want = b"".join(w.to_bytes(2, "little") for e in (sp["04148F"], sp["0414B3"])
                    for w in side_words(dict(e, jp=e["en"]), a))
    assert out[target:target + len(want)] == want
    assert out[0x04148F:0x0414C9] == rom[0x04148F:0x0414C9]
    short = b"".join(w.to_bytes(2, "little") for w in side_words(dict(sp["041449"], jp=sp["041449"]["en"]), a))
    assert out[0x041449:0x041449 + len(short)] == short and out[0x041449 + len(short):0x04146D] == \
        rom[0x041449 + len(short):0x04146D]
    sp["04146D"]["en"] = '{FF09:0000}{FF12}"The whole map is clear now!"{FF04}{FF00}'
    with pytest.raises(ValueError, match="no caller"):
        apply_script(rom, files, field="en")
