"""rom_check.py: the build's ROM-level check (phase 7): no byte changes outside the ranges the build means to write.

    from rom_check import allowed_ranges, check_ranges
    python -X utf8 tools/rom_check.py      -> rebuilds nothing; checks build/bounty_en.sfc against the dump

Allowed: every text region and master block of the layout (tools/rom_text.py), the master pointer table, the 24-bit
operands rewritten for relocated side scripts, the expanded banks $F0-$FF (relocated text, VWF code, fonts), and
each hook site of asm/vwf.asm below bank $F0 (a 4-byte `jml`). build.py writes the list to build/romdiff_ranges.txt
and runs tools/romdiff.py on it after assembling; any other changed byte fails the build.
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


def allowed_ranges(data):
    """[(start, end)) from the apply_script layout `data`."""
    out = [(b["start"], b["end"]) for b in data["master"]["blocks"]]
    out += [(r["start"], r["end"]) for r in data["regions"]]
    out.append((MASTER_TABLE, MASTER_TABLE + 3 * len(data["master"]["slots"])))
    out += [(p, p + 3) for r in data.get("relocs", ()) for p in r["refs"]]
    out += [(h, h + HOOK_BYTES) for h in hook_sites()]
    out.append(EXPANDED)
    return sorted(out)


def write_ranges(ranges, path):
    path.write_text("".join("%X-%X\n" % (s, e - 1) for s, e in ranges if e > s), encoding="utf-8")


def check_ranges(orig_path, built_path, ranges, ranges_path):
    """Run tools/romdiff.py; returns (exit code, its output)."""
    write_ranges(ranges, ranges_path)
    args = [ln for ln in ranges_path.read_text(encoding="utf-8").split()]
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "romdiff.py"), str(orig_path),
                        str(built_path), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


if __name__ == "__main__":
    from script_text import apply_script, load
    orig = ROOT / "rom" / "Bounty Sword (Japan).sfc"
    data = apply_script(orig.read_bytes(), load(), field="en", tags=True)
    code, text = check_ranges(orig, ROOT / "build" / "bounty_en.sfc", allowed_ranges(data),
                              ROOT / "build" / "romdiff_ranges.txt")
    print(text)
    sys.exit(code)
