"""build.py: the one build entry point.

    python -X utf8 build.py              -> build/bounty_en.sfc
    python -X utf8 build.py --identity   -> also fail unless the output equals the original dump byte for byte
    python -X utf8 build.py --dump [--force]  -> write script/*.json from the ROM (only missing files unless --force)

Checks the dump against rom.sha1 first. Unpacks every text structure (tools/rom_text.py), puts each script/ entry's
`en` back in (an empty `en` keeps its `jp`; tools/script_text.py) and repacks.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

from check_rom import check  # noqa: E402
from rom_text import WordCodec, repack  # noqa: E402
from script_text import SCRIPT, apply_script, dump, load  # noqa: E402

ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"
OUT = ROOT / "build" / "bounty_en.sfc"


def build(out=OUT):
    check()
    rom = ORIG.read_bytes()
    if not any(SCRIPT.glob("*.json")):
        sys.exit("script/ is empty: run build.py --dump first")
    data = apply_script(rom, load(SCRIPT), field="en")
    built = repack(rom, data, WordCodec())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(built)
    return rom, built


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="fail unless the output is byte-identical to the dump")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--dump", action="store_true", help="write missing script/*.json files from the ROM and stop")
    ap.add_argument("--force", action="store_true", help="with --dump: overwrite existing files (loses English)")
    ap.add_argument("--refresh", action="store_true",
                    help="with --dump: re-render jp in existing files after a table change, keeping en")
    a = ap.parse_args()
    if a.dump:
        check()
        written, requeue = dump(ORIG.read_bytes(), force=a.force, refresh=a.refresh)
        print(f"wrote {len(written)} file(s) to script/" + (": " + " ".join(written) if written else
              " (all exist; --refresh updates jp, --force overwrites)"))
        if requeue:
            print(f"{len(requeue)} translated entries have new jp; re-check them: {' '.join(requeue)}")
        return
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
