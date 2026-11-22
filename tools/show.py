"""Show script entries by id: file, kind, JP page view and English pages (master) or JP/en (side tables).

    python -X utf8 tools/show.py 24E4A4 0EF856 [...]      # ids as in script/*.json
    python -X utf8 tools/show.py --grep "armor"           # entries whose English contains the text (case-insensitive)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def entries():
    for path in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            yield path.name, e


def show(name, e):
    print(f"== {e['id']}  {name}  kind={e.get('kind', 'text')} width={e.get('width', '')}")
    if e.get("pages"):
        import batches
        import pages
        jp = pages.jp_view(e["jp"], batches.NAMES).split(" ‖ ")
        en = [p.strip() for p in e["pages"].split("||")]
        for n in range(max(len(jp), len(en))):
            print(f"  p{n + 1} JP {jp[n] if n < len(jp) else ''}")
            print(f"  p{n + 1} EN {en[n] if n < len(en) else ''}")
    else:
        print("  JP", repr(e["jp"]))
        print("  EN", repr(e.get("en", "")))


def main(argv):
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "--grep":
        needle = argv[1].lower()
        for name, e in entries():
            if needle in (e.get("en") or "").lower():
                show(name, e)
        return 0
    want = {a.upper() for a in argv}
    for name, e in entries():
        if e["id"].upper() in want:
            show(name, e)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
