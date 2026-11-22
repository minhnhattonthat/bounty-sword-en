"""Phase 8 gate: every choice box and centred menu box measured with the skill's inkbox.py.

    python -X utf8 tools/inkbox_all.py [--shoot] [--only RE] [--jobs 4] [--rom build/bounty_en.sfc]

Rows live in docs/inkbox.tsv (name, scene, vars, route, frames, shot, rects, mode, note):
  scene/vars/route/frames  how to reach the box from a cold boot (tools/debug/warp.lua; vars are |-separated K=V
                           passed as --var, e.g. KEEP=true|AFTER='6 a;80 -' for keys after SCENE_OK; route is a
                           tools/routes file of absolute frames, which replaces the scene's own keys)
  shot                     the frame to measure in the run dir (proof.png, f001600.png ...)
  rects                    x,y,w,h inside one box each (space-separated), cut so the cursor is outside them
  mode   centre  the English ink is centred in each rect (inkbox.py, --tol 2)
         match   the box is laid out flush (cursor lists, left-aligned labels): the English ink starts within 2 px
                 of the Japanese ink in the same rect on the original ROM, and stays off the rect's right edge
         options after the mode: side=right (compare right edges), ink=R,G,B diff=N (text over sprites)
--shoot runs the warps (English into work/qa/ink/<name>_en, original into <name>_jp for match rows); without it the
existing shots are measured. Exit 1 if any row fails or a shot is missing. Report: work/qa/ink/report.tsv.
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

sys.path.insert(0, SCRIPTS)
from inkbox import margins  # noqa: E402
from sheet import read_png  # noqa: E402

TABLE = ROOT / "docs" / "inkbox.tsv"
OUT = ROOT / "work" / "qa" / "ink"
ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"
COLS = ["name", "scene", "vars", "route", "frames", "shot", "rects", "mode", "note"]
TOL = 2


def load(path=TABLE):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        assert list(r) == COLS and None not in r.values(), f"bad row in {path}: {r}"
        assert r["mode"].split()[0] in ("centre", "match"), r
    return rows


def options(row):
    """mode tail: `side=right` (match the right edges: a label set flush against a fixed digit), `ink=R,G,B` and
    `diff=N` (inkbox.py --ink/--diff, for text over sprites or gradients)."""
    opts = dict(o.split("=", 1) for o in row["mode"].split()[1:])
    ink = tuple(int(v) for v in opts["ink"].split(",")) if "ink" in opts else None
    return opts.get("side", "left"), ink, int(opts.get("diff", 40))


def rects(row):
    return [tuple(int(v) for v in r.split(",")) for r in row["rects"].split()]


def run_key(row):
    return row["scene"], row["vars"], row["route"], row["frames"]


def run_dirs(rows):
    """Rows with the same warp share one run: {key: dir stem} (the first such row's name)."""
    stems = {}
    for r in rows:
        stems.setdefault(run_key(r), r["name"])
    return stems


def shots(row, stem):
    """(English shot, original shot): `shot` is one name, or `en.png|jp.png` when the two ROMs differ in timing."""
    en, _, jp = row["shot"].partition("|")
    return OUT / f"{stem}_en" / en, OUT / f"{stem}_jp" / (jp or en)


def shoot(row, stem, rom, tag):
    d = OUT / f"{stem}_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.png"):
        old.unlink()
    cmd = [sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "emu.py"), str(rom), "--out", str(d),
           "--frames", row["frames"] or "9000", "--timeout", "900", "--shot-every", "20",
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{row['scene']}'"]
    for v in filter(None, row["vars"].split("|")):
        cmd += ["--var", v.strip()]
    if row["route"]:
        cmd += ["--route", str(ROOT / row["route"])]
    with open(d / "run.out", "w", encoding="utf-8") as f:
        code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    shutil.rmtree(d / "_mesen", ignore_errors=True)  # emu.py's ~95 MB emulator copy per run
    return code


def measure(path, rs, ink=None, diff=40):
    w, h, bpp, px = read_png(str(path))
    return [margins(px, bpp, r, diff, None, ink) for r in rs]


def judge(row, stem):
    rs = rects(row)
    side, ink, diff = options(row)
    k = 1 if side == "right" else 0
    en, jp = shots(row, stem)
    if not en.exists():
        return False, f"missing {en.relative_to(ROOT)}"
    me = measure(en, rs, ink, diff)
    notes, ok = [], True
    if row["mode"].startswith("centre"):
        for r, m in zip(rs, me):
            good = m is not None and abs(m[0] - m[1]) <= TOL
            ok &= good
            notes.append(f"{r}: " + ("no ink" if m is None else f"L{m[0]} R{m[1]}") + ("" if good else " OFF"))
    else:
        if not jp.exists():
            return False, f"missing {jp.relative_to(ROOT)}"
        mj = measure(jp, rs, ink, diff)
        for r, m, j in zip(rs, me, mj):
            good = m is not None and j is not None and abs(m[k] - j[k]) <= TOL and m[1 - k] > 0
            ok &= good
            notes.append(f"{r}: en " + ("no ink" if m is None else f"L{m[0]} R{m[1]}") +
                         " jp " + ("no ink" if j is None else f"L{j[0]} R{j[1]}") + ("" if good else " OFF"))
    return ok, "; ".join(notes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shoot", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--rom", default=str(ROOT / "build" / "bounty_en.sfc"))
    a = ap.parse_args()
    every = load()
    stems = run_dirs(every)
    rows = [r for r in every if re.search(a.only, r["name"])]
    if a.shoot:
        jobs = {}
        for r in rows:
            stem = stems[run_key(r)]
            jobs[(stem, "en")] = (r, stem, a.rom, "en")
            if r["mode"].startswith("match"):
                jobs[(stem, "jp")] = (r, stem, ORIG, "jp")
        with ThreadPoolExecutor(a.jobs) as ex:
            for (stem, tag), code in zip(jobs, ex.map(lambda j: shoot(*j), jobs.values())):
                if code:
                    print(f"{stem}_{tag}: emu.py exit {code}")
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    with open(OUT / "report.tsv", "w", encoding="utf-8", newline="") as f:
        for r in rows:
            ok, note = judge(r, stems[run_key(r)])
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {r['name']}: {note}")
            f.write(f"{r['name']}\t{'ok' if ok else 'FAIL'}\t{note}\n")
    print(f"{len(rows) - bad}/{len(rows)} boxes ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
