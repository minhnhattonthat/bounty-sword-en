"""menu_map.py: which screens show which cells of a C1 grid string (docs/re/vwf.md "Widening a menu slice").

    python -X utf8 tools/re/menu_map.py 01C894 [--rom PATH]

For the string at the given file offset: every C8 window script that draws it (op 02 base16 ptr24) and the VRAM
tile base its op 0A DMA gives, every C3 script that runs that window script (`24 00 ptr24`), and, after each, the
window defs (`2D 00 ptr24`), layouts (`27 00 ptr24`, C5 records `40 pos16 n 02 tile16`) and op 21 boxes up to the
next window script call. Each record is printed with the string cells it shows (or the other string drawn there).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
ROM = os.path.join(ROOT, 'rom', 'Bounty Sword (Japan).sfc')


def cpu(off):
    return off | 0xC00000


def off(addr):
    return addr & 0x3FFFFF


def entries():
    out = {}
    for f in ('menus', 'windows', 'menus_c'):
        for e in json.load(open(os.path.join(ROOT, 'script', f + '.json'), encoding='utf8')):
            if e.get('kind') == 'text':
                out[int(e['id'], 16)] = e
    return out


def slot_of(start, k):
    t = (start & 0xF) + k
    return (start & ~0xF) + (t // 16) * 0x20 + t % 16


def window_scripts(rom, sid):
    """[(op02 offset, script start guess, base slot, tile base, [(base, string) drawn by the same script])]."""
    out = []
    ptr = cpu(sid).to_bytes(3, 'little')
    for m in re.finditer(re.escape(b'\x02') + b'..' + re.escape(ptr), rom[0x080000:0x090000], re.S):
        p = 0x080000 + m.start()
        # walk back over earlier op 02s of the same script, forward to its op 0A
        s = p
        while rom[s - 6] == 0x02 and rom[s - 1] == 0xC1:
            s -= 6
        q, draws, tile = s, [], None
        while rom[q] == 0x02:
            draws.append((rom[q + 1] | rom[q + 2] << 8, off(int.from_bytes(rom[q + 3:q + 6], 'little'))))
            q += 6
        while rom[q] not in (0x00, 0x0A) and q < s + 64:
            q += 1
        if rom[q] == 0x0A and rom[q + 3] == 0x7E:
            tile = (rom[q + 4] | rom[q + 5] << 8) // 16
        base = rom[p + 1] | rom[p + 2] << 8
        out.append((p, s, base, tile, draws))
    return out


def callers(rom, script):
    ptr = cpu(script).to_bytes(3, 'little')
    return [m.start() for m in re.finditer(re.escape(b'\x24\x00' + ptr), rom)]


def layout(rom, p):
    recs = []
    while rom[p] == 0x40 and rom[p + 4] == 0x02:
        pos = rom[p + 1] | rom[p + 2] << 8
        recs.append((p, pos // 64, (pos % 64) // 2, rom[p + 3], rom[p + 5] | rom[p + 6] << 8))
        p += 7
    return recs, p


def cell_of(draws, tile_base, tile, strings):
    for base, s in draws:
        e = strings.get(s)
        n = e['width'] if e else 32
        for k in range(n):
            if tile_base + slot_of(base, k) == tile:
                return s, k
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sid')
    ap.add_argument('--rom', default=ROM)
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    sid = int(a.sid, 16)
    strings = entries()
    for p, s, base, tile, draws in window_scripts(rom, sid):
        if tile is None:
            print(f"window script C8:{s & 0xFFFF:04X} (op 02 at {p:06X}): no op 0A DMA after it, tiles unknown")
            tile = -0x1000
        print(f"window script C8:{s & 0xFFFF:04X} (op 02 at {p:06X}) base slot {base:02X}, tiles from {tile:03X}; draws "
              + ", ".join(f"{d:06X}@{b:02X}" for b, d in draws))
        for c in callers(rom, s):
            print(f"  C3 caller {c:06X}")
            q = c + 6
            end = q + 160
            while q < end:
                op = rom[q] | rom[q + 1] << 8
                if op == 0x24 and q > c + 12:     # the next window (a second script right after is the same one)
                    break
                if op == 0x2D:
                    d = off(int.from_bytes(rom[q + 2:q + 5], 'little'))
                    print(f"    window def {d:06X}: {rom[d:d + 12].hex(' ')}")
                elif op == 0x27:
                    d = off(int.from_bytes(rom[q + 2:q + 5], 'little'))
                    recs, e = layout(rom, d)
                    print(f"    layout {d:06X} (ends {e:06X}: {rom[e:e + 3].hex(' ')})")
                    for r, row, col, n, t in recs:
                        s2, k = cell_of(draws, tile, t, strings)
                        what = (f"{s2:06X} cells {k}-{k + n - 1}" if s2 is not None else "other tiles")
                        if s2 is not None and s2 in strings:
                            jp = strings[s2]['jp'][k:k + n]
                            what += f" {jp}"
                        print(f"      {r:06X} r{row} c{col} n{n} t{t:03X}  {what}")
                elif op == 0x21:
                    print(f"    op 21 at {q:06X}: {rom[q:q + 6].hex(' ')}")
                q += 1


if __name__ == '__main__':
    main()
