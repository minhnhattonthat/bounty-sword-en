"""Phase 8 stress saves: build every case from a save this ROM writes, then route each one through the camp menus.

    python -X utf8 tools/debug/stress.py [ROM] [--jobs 4] [--only RE]

Cases (save.py edits of file 2; field map in docs/re/debug.md §Save RAM):
  max   widest hero name WWWWWW, gold 65535 (u16 max), widest gear (Hatamoto Blade, Kongo Bracelet) and the four
        widest Pack items by rendered px (Ancient Grimoire, Hermes Sandals, Yorishiro Charm, Motion Stopper)
  min   1-letter name W, gold 0, empty Pack (None)
  one   gold 1, a single Pack item
Each case boots with --sav through the load_file2 scene (title -> Load -> file 2 -> camp) and then runs every ROUTE
(camp box with the gold, party status, items, file menu). The shop's gold box is reached by the town_weapon_shop warp
with the gold held by tools/lua/pokeloop.lua (a loaded save can't reach a town). Output: work/qa/stress/<case>_<route>/
(shots every 100 frames + last.png = the final frame), and work/qa/stress/sheets/sheet*.png of all last.png for the
visual-QA gate (qa_gate.py init work/qa/stress/manifest.tsv work/qa/stress --glob "sheets/sheet*.png" --build ROM).
"""
import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
EMU = PY + [str(Path(SKILL) / "scripts" / "emu.py")]
SHEET = PY + [str(Path(SKILL) / "scripts" / "sheet.py")]
WARP = str(ROOT / "tools" / "debug" / "warp.lua")
POKE = str(ROOT / "tools" / "lua" / "pokeloop.lua")
SAVES = ROOT / "work" / "saves"
OUT = ROOT / "work" / "qa" / "stress"

CASES = {  # name: save.py edit arguments
    "max": ["--name", "ＷＷＷＷＷＷ", "--gold", "65535", "--gear", "16,82", "--pack", "158,129,126,138"],
    "min": ["--name", "Ｗ", "--gold", "0", "--pack", "0,0,0,0"],
    "one": ["--gold", "1", "--pack", "94,0,0,0"],
}
LOADED = 3254  # load_file2 reaches SCENE_OK here; the camp shows the gold box
ROUTES = {  # name: (keys after the camp is up, frames to run)
    "camp": ("100 -", LOADED + 200),
    "status": ("200 -;6 a;200 -;6 down;40 -;6 a;200 -;6 a;250 -", LOADED + 1300),
    "items": ("200 -;6 down;40 -;6 down;40 -;6 a;200 -;6 a;200 -;6 a;200 -;6 a;200 -", LOADED + 1500),
    "file": ("200 -;" + "6 down;40 -;" * 6 + "6 a;200 -;6 a;250 -", LOADED + 1300),
}
SHOP = {"shop_max": "FFFF", "shop_zero": "0000", "shop_one": "0100"}  # gold held in the weapon shop warp


def make_saves(rom):
    # base_en.srm: written by this build through the camp_save scene, so file 1 holds the English default name
    # (work/saves/base.srm comes from save_test.py on the original ROM and says ソード).
    base = SAVES / "base_en.srm"
    name, ok = run(("save_base_en", ["--frames", "5000", "--shot-every", "500", "--script", WARP, "--var",
                                     "SCENE='camp_save'"]), rom)
    srm = next((OUT / name).glob("*.srm"), None)
    if not ok or not srm:
        raise SystemExit("could not make base_en.srm with the camp_save scene")
    SAVES.mkdir(parents=True, exist_ok=True)
    shutil.copy(srm, base)
    for case, args in CASES.items():
        cmd = PY + [str(ROOT / "tools" / "debug" / "save.py"), "edit", str(base), str(SAVES / f"stress_{case}.srm"),
                    "--slot", "2", "--from-slot", "1", "--map", "31", *args]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def run(job, rom):
    name, cmd = job
    out = OUT / name
    if out.exists():
        shutil.rmtree(out)
    with open(str(out) + ".out", "w", encoding="utf-8") as f:
        subprocess.run(EMU + [str(rom), "--out", str(out), "--timeout", "900"] + cmd, stdout=f,
                       stderr=subprocess.STDOUT, check=False)
    shots = sorted(out.glob("f*.png"))
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = "SCENE_OK" in log and bool(shots)
    if shots:
        shutil.copy(shots[-1], out / "last.png")
    shutil.rmtree(out / "_mesen", ignore_errors=True)
    return name, ok


def jobs():
    for case in CASES:
        for route, (keys, frames) in ROUTES.items():
            yield f"{case}_{route}", ["--sav", str(SAVES / f"stress_{case}.srm"), "--frames", str(frames),
                                      "--shot-every", "100", "--script", WARP, "--var", "SCENE='load_file2'",
                                      "--var", "KEEP=1", "--var", f"AFTER='{keys}'"]
    for name, gold in SHOP.items():
        yield name, ["--frames", "1700", "--shot-every", "100", "--script", WARP, "--var",
                     "SCENE='town_weapon_shop'", "--var", "KEEP=1", "--script", POKE, "--var",
                     f"HOLDPOKE='7FFCB0:{gold}'", "--var", "POKE_FROM=600"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "bounty_en.sfc"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="regex on the job name")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    make_saves(a.rom)
    todo = [j for j in jobs() if not a.only or re.search(a.only, j[0])]
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda j: run(j, a.rom), todo))
    bad = [n for n, ok in results if not ok]
    for n, ok in results:
        print(("ok   " if ok else "FAIL ") + n)
    lasts = sorted(str(p) for p in OUT.glob("*/last.png") if p.parent.name != "save_base_en")
    if lasts:
        (OUT / "sheets").mkdir(exist_ok=True)
        subprocess.run(SHEET + lasts + ["--div", "1", "--cols", "4", "--max", "12", "--out",
                                        str(OUT / "sheets" / "sheet.png")], check=True)
    print(f"{len(results) - len(bad)}/{len(results)} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
