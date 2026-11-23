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
import json
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


def _entries():
    """{table: sorted [(file offset, entry)]} from script/, and the keep_jp ids."""
    out = {}
    for path in (ROOT / "script").glob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(doc, list):
            out[path.stem] = sorted((int(e["id"], 16), e) for e in doc if re.fullmatch(r"[0-9A-F]{6}", e["id"]))
    keep = {ln.split("\t")[0] for ln in (ROOT / "script" / "keep_jp.txt").read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#")}
    return out, keep


ENTRIES = None


def classify(off):
    """A run inside an extracted region is known only through its entry: translated (`en` set: the English lives
    elsewhere, the old bytes are a tail or unreachable) or keep-listed. A run in an untranslated or `data` entry is
    UNEXPLAINED: the level-up talk 0414C9 sat in system_prompts as data and a region-only rule whitelisted it."""
    global ENTRIES
    ENTRIES = ENTRIES or _entries()
    tables, keep = ENTRIES
    for name, start, end in rom_text.REGIONS:
        if start <= off < end:
            ids = [(o, e) for o, e in tables.get(name, []) if o <= off]
            if not ids:
                return f"UNEXPLAINED {name} before its first entry"
            o, e = ids[-1]
            if e["id"] in keep:
                return f"region {name} {e['id']} keep"
            if e.get("kind", "text") == "text" and e.get("en"):
                return f"region {name} {e['id']} translated"
            return f"UNEXPLAINED {name} {e['id']} {e.get('kind', 'text')} without English"
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
    bad = [r for r in rows if r[3].startswith("UNEXPLAINED")]
    for off, n, txt, c in bad:
        print(f"{off:06X}\t{n}\t{c}\t{txt}")
    if a.write and bad:
        sys.exit(f"{len(bad)} UNEXPLAINED runs: translate, keep-list or re-split them before writing the list")
    if a.write:
        KNOWN.write_text("".join(f"{off:06X}\t{c}\t{txt}\n" for off, n, txt, c in rows), encoding="utf-8",
                         newline="\n")
        print(f"wrote {KNOWN} ({len(rows)} runs)")


if __name__ == "__main__":
    main()
