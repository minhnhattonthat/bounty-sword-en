"""List the strings a textcover report says were never shown, grouped by script table, with their text.

    python -X utf8 tools/debug/unshown.py work/tc_now.out [--table NAME] [--full]

The report is the stdout of textcover.py ("NEVER SHOWN  <id>  <addr>" lines). Reads script/*.json for jp/en.
"""
import argparse
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_strings():
    out = {}
    for path in glob.glob(os.path.join(ROOT, "script", "*.json")):
        table = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf8") as f:
            for e in json.load(f):
                out[e["id"]] = (table, e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--table")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    strings = load_strings()
    groups = collections.defaultdict(list)
    with open(a.report, encoding="utf8") as f:
        for line in f:
            m = re.match(r"NEVER SHOWN\s+(\S+)\s+(\S+)", line)
            if m:
                table, e = strings.get(m.group(1), ("?", {}))
                groups[table].append((m.group(1), m.group(2), e))
    for table in sorted(groups, key=lambda t: -len(groups[t])):
        if a.table and table != a.table:
            continue
        print(f"== {table} {len(groups[table])}")
        if not (a.full or a.table):
            continue
        for sid, addr, e in groups[table]:
            print(f"{sid} {addr} | {e.get('jp', '')[:50]} | {e.get('en', '')[:70]}")


if __name__ == "__main__":
    main()
