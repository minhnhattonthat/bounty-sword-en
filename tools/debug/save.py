"""Bounty Sword save editor (8 KB SRAM, 3 files). Layout in docs/re/debug.md §Save RAM (from the save routine C1:4940).

    python -X utf8 tools/debug/save.py info SAVE.srm
    python -X utf8 tools/debug/save.py edit BASE.srm OUT.srm [--slot 1] [--map 31] [--name ＷＷＷＷＷＷ]
                                       [--poke OFF=HEXBYTES ...] [--from-slot N]
    python -X utf8 tools/debug/save.py --selftest

Always start from a game-written save (work/saves/base.srm, made by the camp_save warp scene). `edit` copies the
slot (or --from-slot), applies the edits, marks the file used and rewrites its checksum. --slot counts from 1 like the
game's file menu. --name takes any characters in tbl/jp.tbl; ASCII letters/digits become the full-width ones.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TBL = ROOT / "tbl" / "jp.tbl"

SRAM_SIZE = 0x2000
SLOT_BASE = (0x000B, 0x0AAB, 0x154B)   # $30:600B / 6AAB / 754B (pointer table C1:4933)
SLOT_LEN = 0x0AA0                       # copy of WRAM $7F:F4CB-$7F:FF6A
CSUM = (0x0004, 0x0006, 0x0008)         # 16-bit sum of the slot's words
USED = 0x000A                           # bit 1 << slot set when the file holds a save (table C1:49E8)
WRAM_BASE = 0x7FF4CB

FIELDS = {  # name: (slot offset, bytes, what); offsets = WRAM address - $7FF4CB
    "name": (0x018, 12, "hero name, 6 16-bit font codes (FF15/FF19-1E print it)"),
    "map": (0x86B, 2, "scenario / map number ($7FFD36), 1-59: next scenario the camp opens"),
}


def checksum(slot_bytes):
    return sum(int.from_bytes(slot_bytes[i:i + 2], "little") for i in range(0, SLOT_LEN, 2)) & 0xFFFF


def load(path):
    d = bytearray(Path(path).read_bytes())
    if len(d) != SRAM_SIZE:
        raise SystemExit(f"{path}: {len(d)} bytes, expected {SRAM_SIZE}")
    return d


def slot(d, i):
    return d[SLOT_BASE[i]:SLOT_BASE[i] + SLOT_LEN]


def fix(d, i):
    d[CSUM[i]:CSUM[i] + 2] = checksum(slot(d, i)).to_bytes(2, "little")
    d[USED] |= 1 << i


def char_codes():
    codes = {}
    for line in TBL.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if len(k) == 4 and len(v) == 1 and v not in codes:
                codes[v] = int.from_bytes(bytes.fromhex(k), "little")
    return codes


def encode_name(text, codes=None):
    codes = codes or char_codes()
    full = "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else c for c in text)
    if len(full) > 6:
        raise SystemExit(f"name {text!r}: 6 characters at most")
    out = bytearray()
    for c in full:
        if c not in codes:
            raise SystemExit(f"name {text!r}: {c!r} is not in {TBL.name}")
        out += codes[c].to_bytes(2, "little")
    return bytes(out.ljust(12, b"\0"))  # the game pads names with word 0000


def decode_name(b, codes=None):
    rev = {v: k for k, v in (codes or char_codes()).items()}
    words = [int.from_bytes(b[i:i + 2], "little") for i in range(0, len(b), 2)]
    return "".join(rev.get(w, "?") for w in words if w)


def info(d):
    codes = char_codes()
    lines = [f"header {d[:4].hex(' ')}  used mask {d[USED]:02X}"]
    for i in range(3):
        s = slot(d, i)
        stored = int.from_bytes(d[CSUM[i]:CSUM[i] + 2], "little")
        used = bool(d[USED] >> i & 1)
        ok = "ok" if checksum(s) == stored else f"BAD (calc {checksum(s):04X})"
        o, n, _ = FIELDS["map"]
        lines.append(f"file {i + 1}: {'used' if used else 'empty'} checksum {stored:04X} {ok}"
                     + (f"  map {int.from_bytes(s[o:o + n], 'little')}  name {decode_name(s[0x18:0x24], codes)}"
                        if used else ""))
    return "\n".join(lines)


def edit(d, i, src=None, map_=None, name=None, pokes=()):
    if src is not None and src != i:
        d[SLOT_BASE[i]:SLOT_BASE[i] + SLOT_LEN] = slot(d, src)
    base = SLOT_BASE[i]
    if map_ is not None:
        o = FIELDS["map"][0]
        d[base + o:base + o + 2] = int(map_).to_bytes(2, "little")
    if name is not None:
        o = FIELDS["name"][0]
        d[base + o:base + o + 12] = encode_name(name)
    for off, data in pokes:
        if off + len(data) > SLOT_LEN:
            raise SystemExit(f"poke {off:X}+{len(data)} runs past the slot")
        d[base + off:base + off + len(data)] = data
    fix(d, i)
    return d


def parse_poke(s):
    off, hexbytes = s.split("=", 1)
    return int(off, 16), bytes.fromhex(hexbytes)


def selftest():
    d = bytearray(SRAM_SIZE)
    for i in range(3):
        fix(d, i)
    assert d[USED] == 7 and d[CSUM[0]:CSUM[0] + 2] == b"\0\0"
    edit(d, 1, map_=31, pokes=[(0x10, b"\x34\x12")])
    s = slot(d, 1)
    assert s[0x86B:0x86D] == b"\x1f\x00"
    # the map word sits at odd offset 0x86B, so its low byte is the high byte of summed word 0x86A
    assert int.from_bytes(d[CSUM[1]:CSUM[1] + 2], "little") == ((31 << 8) + 0x1234) & 0xFFFF
    if TBL.exists():
        assert decode_name(encode_name("ＡＢ1")) == "ＡＢ１"
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return 0
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info")
    p.add_argument("save")
    p = sub.add_parser("edit")
    p.add_argument("base")
    p.add_argument("out")
    p.add_argument("--slot", type=int, default=1, choices=(1, 2, 3))
    p.add_argument("--from-slot", type=int, choices=(1, 2, 3), help="copy this file into --slot first")
    p.add_argument("--map", type=int)
    p.add_argument("--name")
    p.add_argument("--poke", action="append", default=[], type=parse_poke, help="OFF=HEX (slot offset, hex)")
    a = ap.parse_args()
    if a.cmd == "info":
        print(info(load(a.save)))
        return 0
    d = load(a.base)
    edit(d, a.slot - 1, None if a.from_slot is None else a.from_slot - 1, a.map, a.name, a.poke)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_bytes(d)
    print(info(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
