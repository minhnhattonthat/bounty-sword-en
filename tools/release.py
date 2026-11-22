"""release.py: build, gate and package the patch (phase 9; never publishes: that is the user's call).

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure, in this order:
  1. build.py (its own romdiff/overflow gates)             2. tools/check.py (tests + lint)
  3. emu.py --smoke on the build                           4. jp_left.py --known docs/jp_known.txt (tools/jp_known.py)
  5. qa_gate.py check on every work/qa/**/manifest.tsv     6. textcover.py over work/qa/textcover (+ waivers)
  7. no unticked line in docs/polish.md                    8. no template placeholder in README.md
  9. debug tool off: the warp/save tools are Lua + Python outside the ROM; the build must not hold the Lua-only
     debug hooks either (asm/ has no DEBUG switch set)     10. BPS patch from a checksum-fixed copy, re-applied to
     the clean original and compared                       11. zip = patch + README.txt
Output: release/Bounty_Sword_EN_v<version>.{bps,zip} (gitignored). Refuses to overwrite them without --force.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402
import bps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom" / "Bounty Sword (Japan).sfc"
BUILD = ROOT / "build" / "bounty_en.sfc"
OUT = ROOT / "release"
SCRIPTS = Path(SKILL) / "scripts"
PY = [sys.executable, "-X", "utf8"]
# manifest -> its verdict dir (default: verdicts/ next to the manifest)
VERDICTS = {"work/qa/manifest.tsv": "work/qa/verdicts", "work/qa/stress/manifest.tsv": "work/qa/verdicts_stress",
            "work/qa/story/manifest.tsv": "work/qa/story/verdicts"}
PLACEHOLDER = re.compile(r"<(Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][a-z]+ ?/ ")


def step(name, cmd=None, ok=None):
    print(f"== {name}", flush=True)
    if cmd is not None:
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode:
            sys.exit(f"release stopped at '{name}' (exit {r.returncode})")
    elif not ok[0]:
        sys.exit(f"release stopped at '{name}': {ok[1]}")


def hashes(b):
    return {"CRC32": "%08X" % zlib.crc32(b), "MD5": hashlib.md5(b).hexdigest(), "SHA-1": hashlib.sha1(b).hexdigest()}


def readme(version, orig, patched, patch):
    h, p = hashes(orig), hashes(patched)
    return f"""Bounty Sword - English translation patch v{version}
Unofficial fan translation of Bounty Sword (Super Famicom, Pioneer LDC, 1995).
https://github.com/minhnhattonthat/bounty-sword-en

HOW TO PATCH
Apply {patch} (BPS) to your own dump with Flips, beat or https://www.marcrobot.com/RomPatcher.js/.
No pre-patched ROMs are shared, and none may be.

BASE ROM (Japanese, unheadered)
  Bounty Sword (Japan).sfc, {len(orig)} bytes
  CRC32 {h['CRC32']}
  MD5   {h['MD5']}
  SHA-1 {h['SHA-1']}
If your file has a 512-byte copier header, remove it first.

PATCHED ROM
  {len(patched)} bytes, CRC32 {p['CRC32']}, SHA-1 {p['SHA-1']}

NOTES
- Tested in Mesen (MesenCE). Start from a cold boot / new game: savestates made on the Japanese ROM carry the old
  code and font and will show garbage. In-game saves (SRAM) carry over.
- Known issues and bug reports: https://github.com/minhnhattonthat/bounty-sword-en/issues

CREDITS
Translation, hacking and tools: minhnhattonthat. The translation was made with extensive AI assistance
(Claude by Anthropic). Bounty Sword is (c) Pioneer LDC; this patch is not affiliated with them.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing patch/zip")
    a = ap.parse_args(argv)
    name = f"Bounty_Sword_EN_v{a.version}"
    patch, zpath = OUT / f"{name}.bps", OUT / f"{name}.zip"
    if not a.force and (patch.exists() or zpath.exists()):
        sys.exit(f"{patch.name} / {zpath.name} exist: pass --force to rebuild this version")

    step("build", PY + ["build.py"])
    step("tests + lint", PY + ["tools/check.py"])
    step("smoke", PY + [str(SCRIPTS / "emu.py"), str(BUILD), "--out", "work/qa/release_smoke",
                        "--route", "tools/routes/boot.txt", "--smoke"])
    step("jp_left", PY + [str(SCRIPTS / "jp_left.py"), str(BUILD), "--orig", str(ORIG), "--tbl", "tbl/jp.tbl",
                          "--min", "4", "--limit", "40", "--known", "docs/jp_known.txt"])
    manifests = sorted(ROOT.glob("work/qa/**/manifest.tsv"))
    story = ROOT / "work/qa/story/manifest.tsv"
    step("story pass manifest exists", ok=(story in manifests, "run tools/story_chapters.py + qa_gate.py init"))
    for m in manifests:
        rel = m.relative_to(ROOT).as_posix()
        verdicts = VERDICTS.get(rel, (m.parent / "verdicts").relative_to(ROOT).as_posix())
        step(f"qa_gate {rel}", PY + [str(SCRIPTS / "qa_gate.py"), "check", rel, verdicts])
    step("textcover", PY + [str(SCRIPTS / "textcover.py"), "work/qa/textcover", "build/strings.tsv",
                            "--mask", "0x3FFFFF", "--waive", "docs/text_unshown.tsv"])
    polish = (ROOT / "docs/polish.md").read_text(encoding="utf-8")
    open_lines = [l for l in polish.splitlines() if l.startswith("- [ ]")]
    step("polish.md all ticked", ok=(not open_lines, f"{len(open_lines)} unticked line(s)"))
    left = PLACEHOLDER.findall((ROOT / "README.md").read_text(encoding="utf-8"))
    step("README has no template placeholder", ok=(not left, f"placeholders: {left}"))
    asm = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (ROOT / "asm").glob("*.asm"))
    debug_on = re.findall(r"^\s*!?DEBUG\w*\s*=\s*1\b", asm, re.M | re.I)
    step("debug tool off", ok=(not debug_on, f"asm sets {debug_on}"))

    orig = ORIG.read_bytes()
    fixed, _ = bps.snes_checksum(BUILD.read_bytes())
    OUT.mkdir(exist_ok=True)
    patch.write_bytes(bps.make(orig, fixed))
    step("patch re-applies to the clean original", ok=(bps.apply(orig, patch.read_bytes()) == fixed,
                                                       "re-applied patch differs from the build"))
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", readme(a.version, orig, fixed, patch.name))
    with zipfile.ZipFile(zpath) as z:
        names = sorted(z.namelist())
    step("zip holds patch + README only", ok=(names == sorted([patch.name, "README.txt"]), names))
    print(f"release ok: {zpath} ({zpath.stat().st_size} bytes), patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}"
          f", patched sha1 {hashlib.sha1(fixed).hexdigest()}")


if __name__ == "__main__":
    main()
