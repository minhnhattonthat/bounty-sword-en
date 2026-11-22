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


def test_overflow_rejected(rom, data, codec):
    import copy
    d = copy.deepcopy(data)
    d["master"]["blocks"][0]["msgs"][0] += "[0000]" * 0x10000
    with pytest.raises(ValueError, match="overflows"):
        repack(rom, d, codec)
