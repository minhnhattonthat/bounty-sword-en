"""Text coverage of a build (phase 8/9 gate): every master message and side-table string read at least once.

    python -X utf8 tools/debug/textcover_all.py [ROM] [--out work/qa/textcover] [--jobs 6] [--skip-master]
                                              [--skip-tour] [--match RE]

1. DIR/strings.tsv = build/strings.tsv (written by build.py from its own layout: master through the pointer table,
   side tables at their slot or relocated copy). Kept with the run: addresses move on rebuilds.
2. DIR/master: tools/debug/msgcover.py (each of the 2,462 master slots shown once from a hook state).
3. DIR/tour: tools/debug/warp_all.py over every scene with scripts/lua/probes/textcover.lua watching the ranges that
   hold the keys (C0-FF mirror, plus the 00-3F mirror for $8000-$FFFF), so menus, shops, battles and the ceremony
   log the side-table strings they read.
   `--states` refreshes work/states/<scene>.mss from this build.
4. DIR/side: tools/debug/sidecover.py (name and description tables by pointer swap, from those states).
5. scripts/textcover.py DIR DIR/strings.tsv --mask 0x3FFFFF --waive docs/text_unshown.tsv (exit code passed on).
More runs (stress saves, probes) can drop their own `log.txt` folders under DIR before step 5: `--skip-master
--skip-tour --skip-side` only re-reports.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "build" / "bounty_en.sfc"
DEBUG = ROOT / "tools" / "debug"
GAP = 0x800


def ranges(keys):
    """Merged CPU ranges covering every key (file offsets), in the C0-FF mirror and, where the low word is $8000 or
    more, the 00-3F mirror (LoROM-style windows the game may read through with DBR)."""
    offs = sorted({k & 0x3FFFFF for k in keys})
    spans = []
    for o in offs:
        if spans and o - spans[-1][1] <= GAP and o >> 16 == spans[-1][0] >> 16:
            spans[-1][1] = o + 1
        else:
            spans.append([o, o + 1])
    out = []
    for lo, hi in spans:
        out.append(f"{0xC00000 | lo:X}-{0xC00000 | hi:X}")
        if lo & 0xFFFF >= 0x8000:
            out.append(f"{lo:X}-{hi:X}")
    return ",".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", type=Path, default=ROM)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "textcover")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--skip-master", action="store_true")
    ap.add_argument("--skip-tour", action="store_true")
    ap.add_argument("--skip-side", action="store_true")
    ap.add_argument("--match", help="regex on scene names (tour)")
    ap.add_argument("--waive", type=Path, default=ROOT / "docs" / "text_unshown.tsv")
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    strings = out / "strings.tsv"
    if not (a.skip_master and a.skip_tour and a.skip_side):
        shutil.copy(ROOT / "build" / "strings.tsv", strings)
    keys = [int(line.split("\t")[1], 16) for line in strings.read_text(encoding="utf-8").splitlines() if line]
    py = [sys.executable, "-X", "utf8"]
    if not a.skip_master:
        subprocess.run(py + [str(DEBUG / "msgcover.py"), str(a.rom), "--out", str(out / "master"),
                             "--jobs", str(a.jobs)])
    if not a.skip_tour:
        cmd = py + [str(DEBUG / "warp_all.py"), str(a.rom), "--jobs", str(a.jobs), "--out", str(out / "tour"), "--states",
                    "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
                    "--var", f"RANGES='{ranges(keys)}'"]
        if a.match:
            cmd += ["--match", a.match]
        subprocess.run(cmd)
        for d in (out / "tour").glob("*/_mesen"):
            shutil.rmtree(d, ignore_errors=True)
    if not a.skip_side:
        subprocess.run(py + [str(DEBUG / "sidecover.py"), str(a.rom), "--out", str(out / "side"), "--shots"])
    cmd = py + [str(Path(SKILL) / "scripts" / "textcover.py"), str(out), str(strings), "--mask", "0x3FFFFF"]
    if a.waive.exists():
        cmd += ["--waive", str(a.waive)]
    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
