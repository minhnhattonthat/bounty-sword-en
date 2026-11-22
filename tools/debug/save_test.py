"""In-game test of tools/debug/save.py: an edited save must load with the edited values and no corruption message.

    python -X utf8 tools/debug/save_test.py [ROM]

1. work/saves/base.srm: a game-written save (file 1). Made here if missing by the camp_save warp scene
   (camp -> File -> Save -> file 1) and copied out of that run.
2. save.py copies file 1 into file 2 with map 45 and the name ＷＷＷＷＷＷ, fixing the checksum.
3. The load_file2 scene boots with that save, loads file 2 and must reach the camp (mode 6); warp.lua's ASSERT then
   checks $7FFD36 = 45 and the first name word = Ｗ (0x00E7). A bad checksum would stop at the file menu instead.
Exit 0 only when the scene and both checks pass.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Bounty Sword (Japan).sfc"
SAVES = ROOT / "work" / "saves"
EMU = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py")]
WARP = str(ROOT / "tools" / "debug" / "warp.lua")


def emu(rom, out, scene, frames, *extra):
    out = ROOT / "work" / "qa" / out
    if out.exists():
        shutil.rmtree(out)
    cmd = EMU + [str(rom), "--out", str(out), "--frames", str(frames), "--timeout", "600",
                 "--script", WARP, "--var", f"SCENE='{scene}'", *extra]
    with open(str(out) + ".out", "w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False)
    return out, (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""


def main():
    rom = Path(sys.argv[1]) if len(sys.argv) > 1 else ROM
    SAVES.mkdir(parents=True, exist_ok=True)
    base = SAVES / "base.srm"
    if not base.exists():
        out, log = emu(rom, "save_base", "camp_save", 5000)
        srm = next(out.glob("*.srm"), None)
        if "SCENE_OK" not in log or not srm:
            sys.exit("could not make base.srm with the camp_save scene")
        shutil.copy(srm, base)
    edited = SAVES / "edit_map45.srm"
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "save.py"), "edit", str(base),
                    str(edited), "--slot", "2", "--from-slot", "1", "--map", "45", "--name", "WWWWWW"], check=True)
    _, log = emu(rom, "save_test", "load_file2", 8000, "--sav", str(edited),
                 "--var", "ASSERT='7FFD36=45,7FF4E3=0xE7'")
    checks = re.findall(r"ASSERT (\w+)", log)
    ok = "SCENE_OK" in log and checks == ["ok", "ok"]
    print("\n".join(l for l in log.splitlines() if l.startswith(("MODE", "SCENE", "ASSERT"))))
    print("save test", "ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
