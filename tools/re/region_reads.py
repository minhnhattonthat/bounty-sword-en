"""region_reads.py: summarise a regionreads.lua tour per side table (docs/re/text.md §Text inventory).

    python -X utf8 tools/re/region_reads.py [work/qa/rr] [--entries]

For each rom_text.REGIONS table: bytes read, reader PCs (with counts) and the scenes that read it; --entries also
lists, per script entry, whether the tour read it. Input: DIR/<scene>/log.txt with "RR <off> pc=<PC>" lines.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from rom_text import REGIONS  # noqa: E402


def load(d):
    reads = {}  # off -> (pc, scene) first seen
    for log in sorted(Path(d).glob("*/log.txt")):
        for m in re.finditer(r"RR ([0-9A-F]{6}) pc=([0-9A-F]{6})", log.read_text(encoding="utf-8", errors="replace")):
            reads.setdefault(int(m.group(1), 16), (m.group(2), log.parent.name))
    return reads


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default=str(ROOT / "work" / "qa" / "rr"))
    ap.add_argument("--entries", action="store_true")
    a = ap.parse_args()
    reads = load(a.dir)
    entries = None
    if a.entries:
        from script_text import load as load_script
        entries = load_script()
    for name, s, e in REGIONS:
        hit = {o: v for o, v in reads.items() if s <= o < e}
        pcs = collections.Counter(v[0] for v in hit.values())
        scenes = sorted({v[1] for v in hit.values()})
        print(f"{name:17} {s:06X}-{e:06X} read {len(hit):5}/{e - s:5} bytes  pcs {dict(pcs.most_common(4))}  "
              f"scenes {len(scenes)}: {' '.join(scenes[:6])}")
        if entries:
            es = entries.get(name + ".json", [])
            ids = [int(x["id"], 16) for x in es]
            for i, x in enumerate(es):
                a0, a1 = ids[i], ids[i + 1] if i + 1 < len(ids) else e
                n = sum(1 for o in range(a0, a1) if o in hit)
                if n:
                    print(f"   {x['id']} {x.get('kind', '')[:4]} read {n}/{a1 - a0} start {'Y' if a0 in hit else '-'}")


if __name__ == "__main__":
    main()
