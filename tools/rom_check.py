"""rom_check.py: the build's ROM-level check (phase 7): no byte changes outside the ranges the build means to write.

    from rom_check import allowed_ranges, check_ranges
    python -X utf8 tools/rom_check.py      -> rebuilds nothing; checks build/bounty_en.sfc against the dump

Allowed: every text region and master block of the layout (tools/rom_text.py), the master pointer table, the 24-bit
operands rewritten for relocated side scripts, the expanded banks $F0-$FF (relocated text, VWF code, fonts), and
each hook site of asm/vwf.asm below bank $F0 (a 4-byte `jml`), and the header checksum. Regions and banks are ranges
(build/romdiff_ranges.txt); the small scattered writes go in a write log (build/writes.txt, `romdiff.py --writes`),
so two of them overlapping fails too. build.py runs this after assembling; any other changed byte fails the build.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rom_text import MASTER_TABLE  # noqa: E402

ASM = ROOT / "asm" / "vwf.asm"
EXPANDED = (0x300000, 0x400000)
HOOK_BYTES = 4                       # each low-bank hook is one `jml Label`


def hook_sites(asm=ASM):
    """File offsets of the `org $XXXXXX` + `jml` hooks in the game's own banks (HiROM $C0-$EF -> file - $C00000)."""
    lines = asm.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"org \$([0-9A-Fa-f]{6})\b", line.strip())
        if m and int(m.group(1), 16) < 0xF00000:
            nxt = lines[i + 1].split(";")[0].strip()
            if not nxt.startswith("jml "):
                raise ValueError(f"vwf.asm:{i + 2}: hook at ${m.group(1)} is not a single jml")
            out.append(int(m.group(1), 16) - 0xC00000)
    return out


CHECKSUM = (0xFFDC, 0xFFE0)          # HiROM header complement + checksum, recomputed last by build.py


def allowed_ranges(data):
    """[(start, end)) from the apply_script layout `data`: whole text regions and the expanded banks. The small
    scattered writes (pointer table, relocated operands, hooks, checksum) are logged instead: see write_sites."""
    out = [(b["start"], b["end"]) for b in data["master"]["blocks"]]
    out += [(r["start"], r["end"]) for r in data["regions"]]
    out.append(EXPANDED)
    return sorted(out)


def write_sites(data):
    """[(start, end, writer)) of the small writes outside the text regions: romdiff checks them for overlap and
    for changed bytes they don't cover (--writes)."""
    out = [(MASTER_TABLE, MASTER_TABLE + 3 * len(data["master"]["slots"]), "master pointer table")]
    out += [(p, p + 3, f"caller of relocated {r['id']}") for r in data.get("relocs", ()) for p in r["refs"]]
    out += [(h, h + HOOK_BYTES, "vwf.asm hook $%06X" % (h + 0xC00000)) for h in hook_sites()]
    out.append((*CHECKSUM, "header checksum"))
    out += [(o, o + 2 * n, f"default name {en}") for o, n, _, en in default_names()]
    out += [(o, o + len(new), f"byte patch: {note}") for o, _, new, note in byte_patches() + card_patches()]
    return sorted(out)


def card_patches():
    """The part cards drawn in English (tools/card_gfx.py), in byte_patches() form."""
    from card_gfx import patches
    return patches()


BYTE_PATCHES = ROOT / "script" / "byte_patches.tsv"


def byte_patches(path=BYTE_PATCHES):
    """[(offset, original bytes, new bytes, note)] from script/byte_patches.tsv (tilemap scripts and other data)."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else ():
        if line.strip() and not line.startswith("#"):
            off, old, new, note = line.split("\t")[:4]
            old, new = bytes.fromhex(old), bytes.fromhex(new)
            if len(old) != len(new):
                raise ValueError(f"byte patch {off}: original and new differ in length")
            rows.append((int(off, 16), old, new, note))
    return rows


def put_byte_patches(rom, path=BYTE_PATCHES):
    """Write each byte patch into bytearray `rom`; checks the original bytes first."""
    for off, old, new, note in byte_patches(path) + card_patches():
        if rom[off:off + len(old)] != old:
            raise ValueError(f"byte patch at {off:06X} ({note}): ROM holds {rom[off:off + len(old)].hex()}")
        rom[off:off + len(new)] = new


DEFAULT_NAMES = ROOT / "script" / "default_names.tsv"


def default_names(path=DEFAULT_NAMES):
    """[(offset, words, jp, en)] from script/default_names.tsv."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else ():
        if line.strip() and not line.startswith("#"):
            off, n, jp, en = line.split("\t")[:4]
            rows.append((int(off, 16), int(n), jp, en))
    return rows


def put_default_names(rom, codec, path=DEFAULT_NAMES):
    """Write each default name (English codes, zero-padded to its field) into bytearray `rom`; checks the JP first."""
    for off, n, jp, en in default_names(path):
        old = b"".join(w.to_bytes(2, "little") for w in codec.encode(jp))
        if rom[off:off + len(old)] != old:
            raise ValueError(f"default name at {off:06X}: ROM does not hold {jp}")
        words = codec.encode(en)
        if len(words) > n:
            raise ValueError(f"default name {en!r} is {len(words)} words, field holds {n}")
        rom[off:off + 2 * n] = b"".join(w.to_bytes(2, "little") for w in words) + b"\0" * (2 * (n - len(words)))


def write_ranges(ranges, path):
    path.write_text("".join("%X-%X\n" % (s, e - 1) for s, e in ranges if e > s), encoding="utf-8")


def write_log(sites, orig, built, path):
    """One `OFFSET ORIG_HEX NEW_HEX writer` line per write site; unchanged sites are logged too (overlap check)."""
    path.write_text("".join("%X %s %s %s\n" % (s, orig[s:e].hex(), built[s:e].hex(), w.replace("#", ""))
                            for s, e, w in sites), encoding="utf-8")


def check_ranges(orig_path, built_path, ranges, ranges_path, sites=None):
    """Run tools/romdiff.py over the ranges (+ the write log of `sites`); returns (exit code, its output)."""
    write_ranges(ranges, ranges_path)
    args = [ln for ln in ranges_path.read_text(encoding="utf-8").split()]
    if sites is not None:
        log = ranges_path.with_name("writes.txt")
        write_log(sites, Path(orig_path).read_bytes(), Path(built_path).read_bytes(), log)
        args += ["--writes", str(log)]
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "romdiff.py"), str(orig_path),
                        str(built_path), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


if __name__ == "__main__":
    from script_text import apply_script, load
    orig = ROOT / "rom" / "Bounty Sword (Japan).sfc"
    data = apply_script(orig.read_bytes(), load(), field="en", tags=True)
    code, text = check_ranges(orig, ROOT / "build" / "bounty_en.sfc", allowed_ranges(data),
                              ROOT / "build" / "romdiff_ranges.txt", write_sites(data))
    print(text)
    sys.exit(code)
