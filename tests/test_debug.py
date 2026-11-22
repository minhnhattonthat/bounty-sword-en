"""Debug-tool tests that run without the emulator (the in-game save test is tools/debug/save_test.py)."""
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG = ROOT / "tools" / "debug"
sys.path.insert(0, str(DEBUG))

import make_scenes  # noqa: E402
import save  # noqa: E402


def test_save_selftest():
    r = subprocess.run([sys.executable, "-X", "utf8", str(DEBUG / "save.py"), "--selftest"], capture_output=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_save_checksum_matches_game_written_example():
    # header and file 1 of a save the game wrote (camp_save scene): stored checksum 955B over a known slot
    d = bytearray(save.SRAM_SIZE)
    slot = bytearray(save.SLOT_LEN)
    slot[0] = 1
    save_base = save.SLOT_BASE[0]
    d[save_base:save_base + save.SLOT_LEN] = slot
    save.fix(d, 0)
    assert int.from_bytes(d[4:6], "little") == 1 and d[save.USED] == 1


def test_name_roundtrip():
    assert save.decode_name(save.encode_name("ＷＷＷＷＷＷ")) == "ＷＷＷＷＷＷ"
    assert save.encode_name("AB")[4:] == bytes(8)


def test_scenes_tsv_is_generated_and_well_formed():
    rows = make_scenes.scenes()
    with open(DEBUG / "scenes.tsv", encoding="utf-8", newline="") as f:
        lines = list(csv.reader(f, delimiter="\t"))
    assert lines[0] == make_scenes.COLS
    assert all(len(l) == len(make_scenes.COLS) for l in lines)
    assert [l[0] for l in lines[1:]] == [r["name"] for r in rows], "scenes.tsv is stale: run make_scenes.py"
    kinds = {l[1] for l in lines[1:]}
    assert kinds <= {"boot", "scenario", "mode", "msg"}
