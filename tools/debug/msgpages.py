"""Show one master message page by page: warp.lua's `msg` scene with KEEP, A pressed every GAP frames.

    python -X utf8 tools/debug/msgpages.py ID|SLOT [--rom build/bounty_en.sfc] [--pages 12] [--gap 90]

Writes work/qa/msg_<ID>/ (one shot every 30 frames) and a contact sheet; prints the folder. Use it for polish
checks ("check the box flow in game"); the slot is looked up in script/*.json when an entry id is given.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def slot_of(key):
    for path in (ROOT / "script").glob("master_*.json"):
        for e in json.loads(path.read_text(encoding="utf-8")):
            if e["id"].upper() == key.upper() and e.get("slots"):
                return e["slots"][0]
    return int(key)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("key")
    ap.add_argument("--rom", default="build/bounty_en.sfc")
    ap.add_argument("--pages", type=int, default=12)
    ap.add_argument("--gap", type=int, default=90)
    a = ap.parse_args()
    slot = slot_of(a.key)
    out = ROOT / "work" / "qa" / f"msg_{a.key}"
    after = ";".join([f"{a.gap} -;6 a"] * a.pages)
    frames = 3000 + a.pages * (a.gap + 6) + 300
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", str(out),
           "--script", "tools/debug/warp.lua", "--var", "SCENE='msg'", "--var", f"MSG={slot}",
           "--var", "KEEP=1", "--var", f"AFTER='{after}'", "--frames", str(frames), "--shot-every", "30", "--sheet"]
    r = subprocess.run(cmd, cwd=ROOT)
    print(f"slot {slot} -> {out}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
