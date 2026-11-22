"""build.py: the one build entry point.

    python -X utf8 build.py              -> build/bounty_en.sfc
    python -X utf8 build.py --identity   -> text repack only (no expansion, no asm); fail unless byte-identical
    python -X utf8 build.py --marker     -> build/bounty_marker.sfc: every text entry replaced by its id marker
    python -X utf8 build.py --dump [--force]  -> write script/*.json from the ROM (only missing files unless --force)

Checks the dump against rom.sha1 first. Unpacks every text structure (tools/rom_text.py), puts each script/ entry's
`en` back in (an empty `en` keeps its `jp`; tools/script_text.py) and repacks, expands the ROM to 4 MB and applies
asm/vwf.asm with asar (English font, VWF).
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

from check_rom import check  # noqa: E402
from font_en import write_bins  # noqa: E402
from marker import marker_files  # noqa: E402
from rom_text import ROM_EXPANDED, WordCodec, repack  # noqa: E402
from script_text import SCRIPT, apply_script, dump, load  # noqa: E402

ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"
BUILD = ROOT / "build"
OUT = BUILD / "bounty_en.sfc"
MARKER_OUT = BUILD / "bounty_marker.sfc"
ASAR = ROOT / "tools" / "asar" / "asar.exe"


def assemble(rom_path):
    """Apply asm/vwf.asm (English font + VWF hooks) with asar; the ROM must already be 4 MB."""
    write_bins(BUILD)
    if not ASAR.exists():
        sys.exit(f"{ASAR} missing: unzip asar191.zip from github.com/RPGHacker/asar/releases into tools/asar/")
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm" / "vwf.asm"), str(rom_path)],
                       capture_output=True, text=True)
    if r.returncode:
        rom_path.unlink(missing_ok=True)      # never leave a stale ROM to test
        sys.exit("asar failed:\n" + r.stdout + r.stderr)


def build(out=OUT, identity=False, marker=False):
    check()
    rom = ORIG.read_bytes()
    if not any(SCRIPT.glob("*.json")):
        sys.exit("script/ is empty: run build.py --dump first")
    files = load(SCRIPT)
    if marker:
        files = marker_files(files)
    data = apply_script(rom, files, field="en")
    built = repack(rom, data, WordCodec())
    out.parent.mkdir(parents=True, exist_ok=True)
    if not identity:
        built += b"\xff" * (ROM_EXPANDED - len(built))
    out.write_bytes(built)
    if not identity:
        assemble(out)
        built = out.read_bytes()
    return rom, built


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="fail unless the output is byte-identical to the dump")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--marker", action="store_true",
                    help="marker build (tools/marker.py): every text entry shows its id -> build/bounty_marker.sfc")
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
    if a.marker and a.out == OUT:
        a.out = MARKER_OUT
    rom, built = build(a.out, identity=a.identity, marker=a.marker)
    diff = sum(1 for x, y in zip(rom, built) if x != y) + abs(len(rom) - len(built))
    print(f"{a.out.relative_to(ROOT) if a.out.is_relative_to(ROOT) else a.out}: {len(built)} bytes, "
          f"sha1 {hashlib.sha1(built).hexdigest()}, {diff} bytes differ from the dump")
    if a.identity and diff:
        sys.exit("identity build FAILED")
    if a.identity:
        print("identical")


if __name__ == "__main__":
    main()
