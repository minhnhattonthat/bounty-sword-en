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
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

from bps import snes_checksum  # noqa: E402
from check_rom import check  # noqa: E402
from font_en import write_bins  # noqa: E402
from marker import marker_files  # noqa: E402
from rom_check import (ASM_FILES, allowed_ranges, check_ranges, default_names, put_byte_patches, put_ff28_tag,  # noqa: E402
                       put_default_names, write_sites)
from rom_text import ROM_EXPANDED, WordCodec, repack  # noqa: E402
from script_text import OVERFLOW, SCRIPT, TAGS, WIDE, TextCodec, apply_script, dump, load, strings_tsv  # noqa: E402
from tag_font import TagFont, speaker_names  # noqa: E402

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
    for asm in ASM_FILES:
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm" / asm), str(rom_path)],
                           capture_output=True, text=True)
        if r.returncode:
            rom_path.unlink(missing_ok=True)      # never leave a stale ROM to test
            sys.exit(f"asar failed on {asm}:\n" + r.stdout + r.stderr)


def speaker_map(built, tf):
    """build/spk_map.bin for asm/speaker_match.asm: 24-byte rows (speaker header words, a unit name's words as the
    build wrote it) for every speaker whose JP name is also a battle unit name (default_names.tsv overrides,
    unit_names), so the battle-map portrait match (C2:5C9B, C2:5CDA) still pairs them; then a $FFFF word."""
    units = {}
    for off, n, jp, _ in default_names():
        units.setdefault(jp, set()).add(bytes(built[off:off + 12]) if n == 6 else None)
    for e in json.loads((SCRIPT / "unit_names.json").read_text(encoding="utf-8")):
        if e.get("kind", "text") == "text" and e.get("en"):
            off = int(e["id"], 16)
            units.setdefault(e["jp"].rstrip("　"), set()).add(bytes(built[off:off + 12]))
    rows = []
    for jp, en in speaker_names().items():
        if tf is None or jp not in units:
            continue
        key = b"".join(w.to_bytes(2, "little") for w in tf.words(en, 6))
        rows += [key + v for v in sorted(v for v in units[jp] if v and v != key)]
    return b"".join(rows) + b"\xff\xff"


def apply_qa(files, overrides):
    """--qa ID=text: replace the `en` of one entry (script syntax) for a stress build of single lines."""
    for item in overrides:
        eid, _, text = item.partition("=")
        hits = [e for es in files.values() for e in es if str(e["id"]).upper() == eid.upper()]
        if len(hits) != 1:
            sys.exit(f"--qa {eid}: {len(hits)} entries have that id")
        hits[0]["en"] = text
    return files


def build(out=OUT, identity=False, marker=False, qa=()):
    check()
    rom = ORIG.read_bytes()
    if not any(SCRIPT.glob("*.json")):
        sys.exit("script/ is empty: run build.py --dump first")
    files = load(SCRIPT)
    if marker:
        files = marker_files(files, rom)
    files = apply_qa(files, qa)
    # identity: repack with no edits; marker: keep one char a cell in tags/labels (they measure the fields)
    data = apply_script(rom, files, field="jp" if identity else "en", tags=not (identity or marker))
    BUILD.mkdir(exist_ok=True)
    (TAGS[0] if TAGS else TagFont()).write(BUILD / "font_tag.bin")
    # asm/loc_label.asm: the 14-cell location labels (D20), 14 words a row, index map-1
    (BUILD / "loc_wide.bin").write_bytes(b"".join(w.to_bytes(2, "little") for row in WIDE["locations"] for w in row))
    if OVERFLOW:     # tags and labels render proportionally since phase 7 (tools/tag_font.py): nothing may overflow
        sys.exit(f"{len(OVERFLOW)} English entries overflow a fixed field: "
                 + " ".join(OVERFLOW[:12]) + (" ..." if len(OVERFLOW) > 12 else ""))
    built = repack(rom, data, WordCodec())
    out.parent.mkdir(parents=True, exist_ok=True)
    if not identity:
        built = bytearray(built)
        if not marker:
            put_default_names(built, TextCodec(True))     # script/default_names.tsv: new-game names in English
            put_byte_patches(built)                       # script/byte_patches.tsv: shop tilemaps etc.
            put_ff28_tag(built)                           # C2:5BFB: world-map/town FF28 name (Thetis)
        built = bytes(built) + b"\xff" * (ROM_EXPANDED - len(built))
        tf = None if marker else (TAGS[0] if TAGS else TagFont())
        (BUILD / "spk_map.bin").write_bytes(speaker_map(built, tf))
    out.write_bytes(built)
    if not identity:
        assemble(out)
        built, _ = snes_checksum(out.read_bytes())     # last write: a valid header checksum for carts/emulators
        out.write_bytes(built)
        code, text = check_ranges(ORIG, out, allowed_ranges(data), BUILD / "romdiff_ranges.txt", write_sites(data))
        if code:
            out.unlink(missing_ok=True)
            sys.exit("romdiff: bytes changed outside the allowed ranges (tools/rom_check.py):\n" + text)
        # text coverage keys of this build (tools/debug/textcover_all.py, scripts/textcover.py)
        keys = BUILD / "strings.tsv" if out == OUT else out.with_suffix(".strings.tsv")
        keys.write_text(strings_tsv(built, data), encoding="utf-8")
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
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="stress build: set one entry's en (script syntax); repeatable; default out build/bounty_qa.sfc")
    a = ap.parse_args()
    if a.dump:
        check()
        written, requeue = dump(ORIG.read_bytes(), force=a.force, refresh=a.refresh)
        print(f"wrote {len(written)} file(s) to script/" + (": " + " ".join(written) if written else
              " (all exist; --refresh updates jp, --force overwrites)"))
        if requeue:
            print(f"{len(requeue)} translated entries have new jp; re-check them: {' '.join(requeue)}")
        return
    if a.qa and a.out == OUT:
        a.out = BUILD / "bounty_qa.sfc"
    elif a.marker and a.out == OUT:
        a.out = MARKER_OUT
    elif a.identity and a.out == OUT:          # never overwrite the English build with the repack check
        a.out = BUILD / "bounty_identity.sfc"
    rom, built = build(a.out, identity=a.identity, marker=a.marker, qa=a.qa)
    diff = sum(1 for x, y in zip(rom, built) if x != y) + abs(len(rom) - len(built))
    print(f"{a.out.relative_to(ROOT) if a.out.is_relative_to(ROOT) else a.out}: {len(built)} bytes, "
          f"sha1 {hashlib.sha1(built).hexdigest()}, {diff} bytes differ from the dump")
    if a.identity and diff:
        sys.exit("identity build FAILED")
    if a.identity:
        print("identical")


if __name__ == "__main__":
    main()
