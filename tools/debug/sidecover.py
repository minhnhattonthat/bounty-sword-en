"""Side-table coverage by pointer swap: every string of the name/description tables drawn once on a build.

    python -X utf8 tools/debug/sidecover.py [ROM] [--out work/qa/textcover/side] [--only items,spells] [--jobs 4]

A tour reaches only the items, classes and spells its save happens to hold. Each JOBS row starts from a warp state
(`work/states/<scene>.mss`, `warp_all.py --states`) on a menu that draws the table, and runs tools/debug/sidecover.lua:
each drawer call that would draw an entry of the table draws the next not-yet-shown entry instead, while KEYS make the
menu redraw. Targets come from build/strings.tsv (this build's own layout); the logs land in OUT/<job>/log.txt, which
tools/debug/textcover_all.py's report picks up. Shots (`round*.png`) show what was drawn.
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

ROM = ROOT / "build" / "bounty_en.sfc"
C1RUN34 = 0x018E90    # `jml C1Run34` (asm/vwf.asm): pointer in $34-$36

# job -> table (script file), state (work/states/<state>.mss), prep (route once, to the menu), keys (route per
# round, makes the menu redraw), hook ("c1run34" or an exec address where the pointer is set), ptr/bank (where its
# low word / bank byte live), shot_delay (frames into a round for the --shots shot)
C1 = {"hook": "c1run34", "ptr": 0x34}
JOBS = {
    "items": dict(C1, table="items", state="camp_items", keys="6 down;40 -"),
    "spells": dict(C1, table="spells", state="camp_party_status", keys="6 down;40 -"),
    "constellations": dict(C1, table="constellations", state="camp_party_status", keys="6 down;40 -"),
    # the save slot list shows each file's hero class (3 calls a draw)
    "classes": dict(C1, table="classes", state="camp_save", prep="30 -;6 down;50 -;6 down;50 -",
                    keys="6 a;60 -;6 b;50 -"),
    "orders": dict(C1, table="orders", state="camp_orders", keys="6 a;60 -;6 b;50 -"),
    # window op 26 (C1:89F4): title record $130E,x * 32 + C8:DF5E, drawn for every unit (record 0 is blank, so `lo`
    # takes the catch range down to it)
    "unit_titles": dict(C1, table="unit_titles", state="camp", lo=0xC8DF5E,
                        prep="20 -;6 a;40 -;6 down;30 -;6 a;40 -;6 select;40 -;6 x;40 -;6 y;40 -;6 r;40 -",
                        keys="6 a;60 -;6 b;50 -", shot_delay=50),
    # Select in the Gear/Pack list opens the item's description (Select again closes it): C3:C504 copies pointer
    # `index` of the table at $7E4A31 to engine B's script pointer ($7E4A37 lo, $7E4A39 bank), then starts it
    # ($7E4A25 = 1 at C3:C52D). The prep route walks the camp item screen into the list.
    "descriptions": dict(table="descriptions", state="camp_items", hook=0xC3C52D, ptr=0x7E4A37, bank=0x7E4A39,
                         prep="30 -;6 a;50 -;6 down;40 -;6 a;50 -;6 down;40 -;6 right;40 -;6 a;50 -;6 down;40 -;"
                              "6 x;40 -;6 y;40 -",
                         keys="6 select;80 -;6 select;60 -", shot_delay=80),
}
# Not a job: swapping engine B's pointer at its word reader (C3:C789, offset $7E4A35 = 0) doesn't take, the reader
# already holds the address (session x). Hook where a script pointer is stored instead, as for descriptions.


DESC_TABLES = (0x0EE459, 0x0EFD28)   # descriptions: 3-byte pointer tables ($CE:E459, $CE:EC58 ..) and text


def heads(rom, table, eid, _cache={}):
    """Swap targets: for descriptions only the entries a 3-byte pointer table reaches (each is `{FF03}` then a
    continuation that FF06-calls the shared sub-strings; swapping a sub-string in alone returns to nowhere). The
    continuations and sub-strings are read on the way. Other tables: every entry."""
    if table != "descriptions":
        return True
    if "desc" not in _cache:
        lo, hi = DESC_TABLES
        _cache["desc"] = {int.from_bytes(rom[p:p + 3], "little") & 0x3FFFFF for p in range(lo, hi)
                          if rom[p + 2] == 0xCE and rom[p - 2:p] != b"\x06\xff"}    # not an FF06 call operand
    return int(eid, 16) in _cache["desc"]


def jml_target(rom, off):
    assert rom[off] == 0x5C, f"no JML at {off:06X}"
    return int.from_bytes(rom[off + 1:off + 4], "little")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", type=Path, default=ROM)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "textcover" / "side")
    ap.add_argument("--only")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--shots", action="store_true")
    a = ap.parse_args()
    rom = a.rom.read_bytes()
    keys = dict(line.split("\t") for line in (ROOT / "build" / "strings.tsv").read_text(encoding="utf-8").splitlines())
    names = a.only.split(",") if a.only else list(JOBS)

    def job(name):
        j = JOBS[name]
        table, hook, ptr = j["table"], j["hook"], j["ptr"]
        entries = json.loads((ROOT / "script" / f"{table}.json").read_text(encoding="utf-8"))
        watch = [keys[e["id"]] for e in entries if e["id"] in keys]
        targets = [keys[e["id"]] for e in entries if e["id"] in keys and heads(rom, table, e["id"])]
        addrs = [int(t, 16) for t in watch]
        lo, hi = min(addrs + [j.get("lo", 0xFFFFFF)]), max(addrs) + 1
        hook_addr = jml_target(rom, C1RUN34) if hook == "c1run34" else hook
        d = a.out / name
        if d.exists():
            shutil.rmtree(d)
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(a.rom), "--out", str(d),
               "--state-in", str(ROOT / "work" / "states" / f"{j['state']}.mss"), "--frames", "60000",
               "--timeout", "1800", "--script", str(ROOT / "tools" / "debug" / "sidecover.lua"),
               "--var", f"HOOK=0x{hook_addr:X}", "--var", f"PTR=0x{ptr:X}", "--var", f"LO=0x{lo:X}",
               "--var", f"HI=0x{hi:X}", "--var", f"TARGETS='{','.join(targets)}'", "--var", f"KEYS='{j['keys']}'"]
        if len(watch) > len(targets):
            cmd += ["--var", f"WATCH='{','.join(sorted(set(watch) - set(targets)))}'"]
        if "bank" in j:
            cmd += ["--var", f"BANK=0x{j['bank']:X}"]
        if "prep" in j:
            cmd += ["--var", f"PREP='{j['prep']}'"]
        if a.shots:
            cmd += ["--var", "SHOT=1"] + (["--var", f"SHOT_DELAY={j['shot_delay']}"] if "shot_delay" in j else [])
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "run.out", "w", encoding="utf-8") as fh:
            code = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT).returncode
        shutil.rmtree(d / "_mesen", ignore_errors=True)
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        done = [line for line in log.splitlines() if line.startswith("SIDECOVER_DONE")]
        return name, code, done[0] if done else "NOT DONE"

    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, code, done in ex.map(job, names):
            print(f"{name:16} exit {code}  {done}")
            bad += code != 0 or not done.startswith("SIDECOVER_DONE")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
