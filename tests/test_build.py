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
    """script/byte_patches.tsv: each shop map shows whole English words of glyph set 01D2B7 (Weapons = tiles C0-C5)."""
    from rom_check import byte_patches
    _, data, _ = built
    patches = byte_patches()
    assert patches, "script/byte_patches.tsv is empty"
    for off, _, new, note in patches:
        assert data[off:off + len(new)] == new, note
    assert data[0x05B230:0x05B237] == bytes.fromhex("408a000602c000")
    assert data[0x32787:0x32791] == b"".join((0x0F00 + ord(c)).to_bytes(2, "little") for c in "Vault")


def test_header_checksum_is_valid(built):
    _, data, _ = built
    total = sum(data[:0xFFDC]) + sum(data[0xFFE0:]) + 0xFF * 2 & 0xFFFF
    check = int.from_bytes(data[0xFFDE:0xFFE0], "little")
    comp = int.from_bytes(data[0xFFDC:0xFFDE], "little")
    assert check == total and comp == check ^ 0xFFFF
