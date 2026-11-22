"""build.py: the one build entry point.

    python -X utf8 build.py              -> build/bounty_en.sfc
    python -X utf8 build.py --identity   -> also fail unless the output equals the original dump byte for byte

Checks the dump against rom.sha1 first. Phase 3: unpack every text structure (tools/rom_text.py) and repack it with
no edits. Later phases apply the English script between the two steps.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

from check_rom import check  # noqa: E402
from rom_text import WordCodec, repack, unpack  # noqa: E402

ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"
OUT = ROOT / "build" / "bounty_en.sfc"


def build(out=OUT):
    check()
    rom = ORIG.read_bytes()
    codec = WordCodec()
    data = unpack(rom, codec)
    built = repack(rom, data, codec)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(built)
    return rom, built


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="fail unless the output is byte-identical to the dump")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    rom, built = build(a.out)
    diff = sum(1 for x, y in zip(rom, built) if x != y) + abs(len(rom) - len(built))
    print(f"{a.out.relative_to(ROOT) if a.out.is_relative_to(ROOT) else a.out}: {len(built)} bytes, "
          f"sha1 {hashlib.sha1(built).hexdigest()}, {diff} bytes differ from the dump")
    if a.identity and diff:
        sys.exit("identity build FAILED")
    if a.identity:
        print("identical")


if __name__ == "__main__":
    main()
