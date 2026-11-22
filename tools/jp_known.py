"""jp_known.py: sort the release build's leftover Japanese runs (`jp_left.py --orig`) into known classes.

    python -X utf8 tools/jp_known.py [--write]      # prints counts + the unclassified runs; --write rewrites docs/jp_known.txt

Classes: `region <table> <entry>` = inside an extracted side-table entry that is data, kept JP (script/keep_jp.txt) or
translated (its English lives elsewhere: relocated script, trampoline copy, or the field was rewritten and a JP tail
stayed); `master` = inside a master block (repacked from its start; the old tail stays); `noise` = outside every
text region and reviewed as code/graphics/data bytes (docs/re/jp_left.md §Worked). The release gate runs jp_left.py
with --known docs/jp_known.txt, so only runs that appear after this list was written fail it. Re-run after a table
change; read every new `outside` run before adding it with --write.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rom_text  # noqa: E402
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KNOWN = ROOT / "docs" / "jp_known.txt"
BUILD = ROOT / "build" / "bounty_en.sfc"
ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"


def runs(built=BUILD, known=None):
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "jp_left.py"), str(built), "--orig", str(ORIG),
           "--tbl", str(ROOT / "tbl" / "jp.tbl"), "--min", "4", "--limit", "0"]
    if known:
        cmd += ["--known", str(known)]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout
    return [(int(m[1], 16), int(m[2]), m[3]) for m in re.finditer(r"^0x([0-9A-F]+)\s+(\d+)B\s+(.*)$", out, re.M)]


def classify(off):
    for name, start, end in rom_text.REGIONS:
        if start <= off < end:
            return f"region {name}"
    blocks = sorted(rom_text.MASTER_BLOCKS)
    if blocks[0] <= off < rom_text.MASTER_TABLE or rom_text.MASTER_END <= off < 0x2B0000:
        return "master"
    return "noise"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", default="noise", help="class prefix whose runs to print (default noise)")
    a = ap.parse_args(argv)
    rows = [(off, n, txt, classify(off)) for off, n, txt in runs()]
    counts = {}
    for *_, c in rows:
        counts[c.split()[0]] = counts.get(c.split()[0], 0) + 1
    print(counts)
    for off, n, txt, c in rows:
        if c.startswith(a.show):
            print(f"{off:06X}\t{n}\t{c}\t{txt}")
    if a.write:
        KNOWN.write_text("".join(f"{off:06X}\t{c}\t{txt}\n" for off, n, txt, c in rows), encoding="utf-8",
                         newline="\n")
        print(f"wrote {KNOWN} ({len(rows)} runs)")


if __name__ == "__main__":
    main()
