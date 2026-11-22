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
5. DIR/gaps, gaps_moves, master/side_a, speakers: what 2-4 missed, swapped in by the report's own gaps (engine B
   scripts and grid strings, FF09 operand tables with the cursor moved, engine A side scripts, speaker rows; see
   `speakers()` and the sidecover jobs with `catch`). `--skip-gaps` leaves it out.
6. scripts/textcover.py DIR DIR/strings.tsv --mask 0x3FFFFF --waive docs/text_unshown.tsv (exit code passed on).
More runs (stress saves, probes) can drop their own `log.txt` folders under DIR before step 6: `--skip-master
--skip-tour --skip-side --skip-gaps` only re-reports.
"""
import argparse
import json
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
    ap.add_argument("--skip-gaps", action="store_true")
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
    cmd = py + [str(Path(SKILL) / "scripts" / "textcover.py"), str(out), str(strings), "--mask", "0x3FFFFF"]
    if a.waive.exists():
        cmd += ["--waive", str(a.waive)]

    def report():
        path = out / "gaps_report.out"
        with open(path, "w", encoding="utf-8") as fh:
            subprocess.run(cmd, stdout=fh)
        return path

    if not a.skip_side:
        subprocess.run(py + [str(DEBUG / "sidecover.py"), str(a.rom), "--out", str(out / "side"), "--shots"])
    if not a.skip_gaps:
        # 5. what steps 2-4 missed, by swapping the gaps in: engine B scripts and grid strings (sidecover), FF09
        # operand tables with the cursor moved (their parents), engine A side scripts (msgcover --side), speaker rows
        rep = report()
        subprocess.run(py + [str(DEBUG / "sidecover.py"), str(a.rom), "--out", str(out / "gaps"), "--only",
                             "engine_b,grids", "--report", str(rep), "--shots"])
        rep = report()
        subprocess.run(py + [str(DEBUG / "sidecover.py"), str(a.rom), "--out", str(out / "gaps_moves"), "--only",
                             "engine_b_moves", "--report", str(rep), "--shots"])
        subprocess.run(py + [str(DEBUG / "msgcover.py"), str(a.rom), "--out", str(out / "master"), "--side",
                             str(report()), "--shots"])
        speakers(a.rom, out, report())
        # sessions aa and ac: the first side job printed "side_a: nothing to do" with 47 engine A side lines
        # unshown in the report (cause not found); the same call afterwards shows them all, so run it once more
        subprocess.run(py + [str(DEBUG / "msgcover.py"), str(a.rom), "--out", str(out / "master"), "--side",
                             str(report()), "--shots"])
    sys.exit(subprocess.run(cmd).returncode)


def speakers(rom, out, rep):
    """Speaker-table rows (C2:5D5D..) are read by the FF15 name match only when a message names that speaker, and
    the master run watches the text banks alone: show one message per unshown row with the probe on the table."""
    unshown = {line.split()[2] for line in rep.read_text(encoding="utf-8").splitlines()
               if line.startswith("NEVER SHOWN")}
    rows = [e for e in json.loads((ROOT / "script" / "speakers.json").read_text(encoding="utf-8"))
            if e["id"] in unshown and e.get("kind") == "text"]
    slots = {}
    for f in sorted((ROOT / "script").glob("master_*.json")):
        for m in json.loads(f.read_text(encoding="utf-8")):
            for e in rows:
                if e["id"] not in slots and m.get("slots") and m["jp"].startswith("{spk}" + e["jp"]):
                    slots[e["id"]] = m["slots"][0]
    lo = min(int(e["id"], 16) for e in json.loads((ROOT / "script" / "speakers.json").read_text(encoding="utf-8")))
    probe = Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"
    for sid, slot in sorted(slots.items()):
        d = out / "speakers" / f"msg_{slot}"
        shutil.rmtree(d, ignore_errors=True)
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out",
                        str(d), "--script", str(DEBUG / "warp.lua"), "--script", str(probe), "--var", "SCENE='msg'",
                        "--var", f"MSG={slot}", "--var", f"RANGES='C{lo:05X}-C{lo + 0x300:05X}'",
                        "--frames", "9000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(d / "_mesen", ignore_errors=True)
    for e in rows:
        if e["id"] not in slots:
            print(f"speaker {e['id']} {e['jp']}: no master message names it")


if __name__ == "__main__":
    main()
