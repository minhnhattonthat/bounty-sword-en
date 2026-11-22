import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Bounty Sword (Japan).sfc"


@pytest.mark.skipif(not ROM.exists(), reason="no ROM in this clone")
def test_rom_matches_sha1():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_rom.py")], cwd=ROOT)
    assert r.returncode == 0


def test_tbl_codec_importable():
    sys.path.insert(0, str(ROOT / "tools"))
    import tbl  # noqa: F401
