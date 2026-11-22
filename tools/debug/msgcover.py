"""Text coverage of the master dialogue: show every master message once on a build and log its first-byte read.

    python -X utf8 tools/debug/msgcover.py [ROM] [--out work/qa/cover] [--jobs 6] [--wait 60] [--shots]
                                         [--first 0 --last 2461]

1. warp.lua's `msg` scene with HOOK_STATE saves DIR/hook.mss where scenario 37's first dialogue starts.
2. `--jobs` emu.py runs of tools/debug/msgcover.lua, each over a slice of the 2,462 slots, load that state per slot,
   swap the slot's pointer in, and log `TEXT <addr>` once the game reads the message's first byte.
3. DIR/strings.tsv (`id<TAB>addr`, one per master entry, from the ROM's own pointer table, so relocation is followed)
   is kept with the run; then `textcover.py DIR DIR/strings.tsv --waive docs/text_unshown.tsv` reports gaps
   (this script runs it and exits with its code).
`--shots` also saves msgNNNN.png (the first box of each message) in each job folder.
"""
import argparse
import concurrent.futures as cf
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402
from rom_text import MASTER_TABLE, MASTER_END  # noqa: E402

ROM = ROOT / "build" / "bounty_en.sfc"
EMU = Path(SKILL) / "scripts" / "emu.py"
DEBUG = ROOT / "tools" / "debug"
SLOTS = (MASTER_END - MASTER_TABLE) // 3


def strings_tsv(rom_bytes):
    """One row per master entry: its id and the CPU address its first slot points to in this ROM."""
    rows = []
    for f in sorted((ROOT / "script").glob("master_*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if not e.get("slots"):
                continue
            p = MASTER_TABLE + 3 * e["slots"][0]
            addr = int.from_bytes(rom_bytes[p:p + 3], "little")
            rows.append(f"{e['id']}\t{addr:06X}")
    return "\n".join(rows) + "\n"


def emu(rom, out, frames, *extra):
    out.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", str(EMU), str(rom), "--out", str(out), "--frames", str(frames),
           "--timeout", "3600", *extra]
    with open(out / "run.out", "w", encoding="utf-8") as fh:
        code = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT).returncode
    shutil.rmtree(out / "_mesen", ignore_errors=True)   # emu.py's 95 MB runtime copy
    return code


# engine A scripts outside the master table (byte scripts and in-place tables): reached by the same pointer swap
SIDE_A = ("battle_prompts", "battle_prompts_b", "system_prompts", "level_up", "target_prompts", "enemy_lost")


def side_job(rom, out, hook, report, wait, shots):
    unshown = {line.split()[2] for line in report.read_text(encoding="utf-8").splitlines()
               if line.startswith("NEVER SHOWN")}
    keys = dict(line.split("\t") for line in (ROOT / "build" / "strings.tsv").read_text(encoding="utf-8").splitlines())
    ptrs = [keys[e["id"]] for t in SIDE_A
            for e in json.loads((ROOT / "script" / f"{t}.json").read_text(encoding="utf-8"))
            if e["id"] in unshown and e["id"] in keys]
    if not ptrs:
        print("side_a: nothing to do")
        return 0
    # each side run gets its own dir (side_a, side_a_2, ..): deleting the last one's logs here un-showed what it showed
    # (sessions aa-af: the re-run in textcover_all wiped the first run's lines); the main master run clears them all
    d = out / "side_a"
    n = 1
    while d.exists():
        n += 1
        d = out / f"side_a_{n}"
    extra = ["--script", str(DEBUG / "msgcover.lua"), "--var", f"HOOK_STATE=[[{hook.as_posix()}]]",
             "--var", f"PTRS='{','.join(ptrs)}'", "--var", f"WAIT={wait}"] + (["--var", "MSGSHOT=1"] if shots else [])
    code = emu(rom, d, (len(ptrs) + 2) * (wait + 10) + 600, *extra)
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    print(f"side_a: exit {code}, {'done' if 'MSGCOVER_DONE' in log else 'NOT DONE'}, "
          f"{log.count(' ok' + chr(10))} ok, {log.count(' miss' + chr(10))} miss of {len(ptrs)}")
    return 0 if "MSGCOVER_DONE" in log else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", type=Path, default=ROM)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "cover")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--wait", type=int, default=60, help="frames per message (default 60)")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--last", type=int, default=SLOTS - 1)
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--waive", type=Path, default=ROOT / "docs" / "text_unshown.tsv")
    ap.add_argument("--side", type=Path, metavar="REPORT",
                    help="textcover.py stdout: swap in its NEVER SHOWN engine A side-table scripts (SIDE_A tables, "
                         "addresses from build/strings.tsv) instead of master slots; one job, writes OUT/side_a")
    a = ap.parse_args()
    rom, out = a.rom.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not a.side:
        (out / "strings.tsv").write_text(strings_tsv(rom.read_bytes()), encoding="utf-8")

    hook = out / "hook.mss"
    if not (a.side and hook.exists()):
        hook.unlink(missing_ok=True)
        code = emu(rom, out / "_hook", 7000, "--script", str(DEBUG / "warp.lua"), "--var", "SCENE='msg'",
                   "--var", f"SCENES=[[{(DEBUG / 'scenes.tsv').as_posix()}]]",
                   "--var", f"HOOK_STATE=[[{hook.as_posix()}]]")
        if not hook.exists():
            sys.exit(f"no hook state (emu.py exit {code}, see {out / '_hook' / 'log.txt'})")

    if a.side:
        sys.exit(side_job(rom, out, hook, a.side, a.wait, a.shots))
    for d in [out / "side_a"] + list(out.glob("side_a_*")):   # side runs of an older build: addresses move
        shutil.rmtree(d, ignore_errors=True)

    n = a.last - a.first + 1
    step = -(-n // a.jobs)
    parts = [(s, min(s + step - 1, a.last)) for s in range(a.first, a.last + 1, step)]

    def job(part):
        lo, hi = part
        d = out / f"slots_{lo:04d}_{hi:04d}"
        if d.exists():
            shutil.rmtree(d)
        extra = ["--script", str(DEBUG / "msgcover.lua"), "--var", f"HOOK_STATE=[[{hook.as_posix()}]]",
                 "--var", f"FIRST={lo}", "--var", f"LAST={hi}", "--var", f"WAIT={a.wait}"]
        if a.shots:
            extra += ["--var", "MSGSHOT=1"]
        code = emu(rom, d, (hi - lo + 2) * (a.wait + 10) + 600, *extra)
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        return d.name, code, "MSGCOVER_DONE" in log, log.count(" ok\n"), log.count(" miss\n")

    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, code, done, ok, miss in ex.map(job, parts):
            print(f"{name}: exit {code}, {'done' if done else 'NOT DONE'}, {ok} ok, {miss} miss")
            bad += not done
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "textcover.py"), str(out),
           str(out / "strings.tsv"), "--mask", "0x3FFFFF"]
    if a.waive.exists():
        cmd += ["--waive", str(a.waive)]
    rc = subprocess.run(cmd).returncode
    sys.exit(1 if bad else rc)


if __name__ == "__main__":
    main()
