"""Run every scene in tools/debug/scenes.tsv (or a subset) from a cold boot and check each one reached its scene.

    python -X utf8 tools/debug/warp_all.py [ROM] [--only NAME,NAME | --match REGEX] [--jobs 4] [--out work/qa/warp]
                                          [--states] [--sheet] [--shot-every 0]

ROM defaults to the original dump. Each scene runs `emu.py ROM --script tools/debug/warp.lua --var SCENE=...` in its
own `--out DIR/<scene>`; a scene passes when its log has `SCENE_OK` (warp.lua logs it once the expected game mode has
held for the row's hold frames; the run then stops). `--states` also saves `work/states/<scene>.mss` at that point
(regenerate them all after code, font or graphics changes). `--sheet` writes DIR/proofs.png from every proof.png.
Writes DIR/summary.tsv (scene, ok, frame, modes seen) and exits 1 if any scene failed.
"""
import argparse
import concurrent.futures as cf
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Bounty Sword (Japan).sfc"
SCENES = ROOT / "tools" / "debug" / "scenes.tsv"


def load_scenes(path=SCENES):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    width = len(rows[0]) if rows else 0
    for r in rows:
        assert len(r) == width and None not in r, f"bad column count in {path}: {r}"
    return rows


def frames_for(row):
    """Generous frame budget: boot rows need their whole route; warps start about f450."""
    hold = int(row["hold"] or 120)
    return int(row.get("frames") or 0) or (hold + 6000)


def run_scene(rom, row, out, states, shot_every, scenes=SCENES, extra=()):
    name = row["name"]
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.png"):
        old.unlink()
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--frames", str(frames_for(row)), "--timeout", "900",
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{name}'",
           "--var", f"SCENES=[[{Path(scenes).resolve().as_posix()}]]"]
    if shot_every:
        cmd += ["--shot-every", str(shot_every)]
    cmd += list(extra)
    if row.get("sav"):
        sav = ROOT / row["sav"]
        if not sav.exists():
            return name, False, "", f"missing {row['sav']} (run tools/debug/save_test.py)", -1
        cmd += ["--sav", str(sav)]
    if states:
        cmd += ["--var", f"WARP_STATE=[[{(ROOT / 'work' / 'states' / (name + '.mss')).as_posix()}]]"]
    with open(d / "run.out", "w", encoding="utf-8") as f:
        code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    m = re.search(r"SCENE_OK \S+ f(\d+)", log)
    modes = " ".join(re.findall(r"MODE (\d+) f\d+", log))
    ok = bool(m) and code == 0 and (d / "proof.png").exists()
    return name, ok, m.group(1) if m else "", modes, code


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROM))
    ap.add_argument("--only", help="comma-separated scene names")
    ap.add_argument("--match", help="regex on scene names")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--scenes", default=str(SCENES), help="scene list (default tools/debug/scenes.tsv)")
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "warp"))
    ap.add_argument("--states", action="store_true", help="save work/states/<scene>.mss at SCENE_OK")
    ap.add_argument("--sheet", action="store_true", help="contact sheet of every proof.png")
    ap.add_argument("--shot-every", type=int, default=0)
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe after warp.lua (repeatable)")
    ap.add_argument("--var", action="append", default=[], help="extra NAME=LUA global for the probes (repeatable)")
    a = ap.parse_args()
    extra = [x for s in a.script for x in ("--script", str(Path(s).resolve()))]
    extra += [x for v in a.var for x in ("--var", v)]

    rows = load_scenes(a.scenes)
    if a.only:
        want = set(a.only.split(","))
        missing = want - {r["name"] for r in rows}
        if missing:
            sys.exit(f"unknown scenes: {sorted(missing)}")
        rows = [r for r in rows if r["name"] in want]
    if a.match:
        rows = [r for r in rows if re.search(a.match, r["name"])]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.states:
        (ROOT / "work" / "states").mkdir(parents=True, exist_ok=True)

    results = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(run_scene, Path(a.rom), r, out, a.states, a.shot_every, a.scenes, extra) for r in rows]
        for fu in cf.as_completed(futs):
            name, ok, frame, modes, code = fu.result()
            results.append((name, ok, frame, modes, code))
            print(f"{'ok  ' if ok else 'FAIL'} {name:20} f{frame or '-':>6} exit {code} modes {modes}", flush=True)
    order = {r["name"]: i for i, r in enumerate(rows)}
    results.sort(key=lambda t: order[t[0]])
    with open(out / "summary.tsv", "w", encoding="utf-8", newline="") as f:
        f.write("scene\tok\tframe\tmodes\n")
        for name, ok, frame, modes, _ in results:
            f.write(f"{name}\t{int(ok)}\t{frame}\t{modes}\n")
    if a.sheet:
        proofs = [str(out / n / "proof.png") for n, ok, *_ in results if ok]
        if proofs:
            subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *proofs,
                            "--div", "2", "--cols", "6", "--max", "36", "--out", str(out / "proofs.png")], check=False)
    bad = [n for n, ok, *_ in results if not ok]
    print(f"{len(results) - len(bad)}/{len(results)} scenes ok" + (f"; failed: {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
