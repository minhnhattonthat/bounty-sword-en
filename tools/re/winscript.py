"""Decode C1 window scripts (interpreter C1:870C, opcode table C1:871A).

    python -X utf8 tools/re/winscript.py C8F3C0 [--count 60]

Each opcode is a byte (even, table index = op/2); its handler reads its arguments with JSR C1:875E (byte) and
C1:8765 (word) from [$30],y. The argument layout is taken from the handler code itself (scanned up to the JMP back
to the loop at C1:870E), so the decoder stays honest about ops it hasn't seen. Op 00 ends the script.
"""
import argparse
import os
import sys

ROM = os.path.join(os.path.dirname(__file__), '..', '..', 'rom', 'Bounty Sword (Japan).sfc')


def off(addr):
    return addr & 0x3FFFFF


def handler_args(rom, h):
    """Return the list of arg sizes (1/2) read by the handler at C1:h, or None if it doesn't look linear."""
    p = off(0xC10000 | h)
    sizes = []
    for _ in range(80):
        b = rom[p]
        if b == 0x20:  # JSR abs
            t = rom[p + 1] | rom[p + 2] << 8
            if t == 0x875E:
                sizes.append(1)
            elif t == 0x8765:
                sizes.append(2)
            p += 3
            continue
        if b == 0x4C:  # JMP abs
            t = rom[p + 1] | rom[p + 2] << 8
            return sizes if t in (0x870E, 0x8719) else sizes
        if b == 0x6B:  # RTL
            return sizes
        p += op_len(rom, p)
    return sizes


# minimal 65816 length table for 16-bit M/X (handlers run with REP #$30)
L1 = {0x18, 0x38, 0x48, 0x68, 0x8A, 0xAA, 0xA8, 0x98, 0xC8, 0x88, 0xE8, 0xCA, 0x0A, 0x4A, 0x3A, 0x1A, 0x5A, 0x7A,
      0xDA, 0xFA, 0x8B, 0xAB, 0x60, 0x6B, 0x40, 0xEB, 0x5B, 0x7B, 0x1B, 0x3B, 0xFB, 0x9B, 0xBB, 0x08, 0x28, 0x0B, 0x2B}
L4 = {0x22, 0x5C, 0x8F, 0xAF, 0x6F, 0x2F, 0x0F, 0x4F, 0xCF, 0xEF, 0x9F, 0xBF, 0x7F, 0x3F, 0x1F, 0x5F, 0xDF, 0xFF}
IMM = {0x09, 0x29, 0x49, 0x69, 0x89, 0xA9, 0xC9, 0xE9, 0xA0, 0xA2, 0xC0, 0xE0}
L3 = {0x20, 0x4C, 0x6C, 0x7C, 0xFC, 0x8D, 0xAD, 0x8E, 0xAE, 0x8C, 0xAC, 0x9C, 0xBD, 0xBC, 0xBE, 0x9D, 0x99, 0xB9,
      0x6D, 0x2D, 0x0D, 0x4D, 0xCD, 0xED, 0xEE, 0xCE, 0x1C, 0x0C, 0x7D, 0x3D, 0xDD, 0xFD, 0x79, 0x39, 0xD9, 0xF9,
      0x1D, 0x5D, 0x19, 0x59, 0xEC, 0xCC, 0x2C, 0x3C, 0x9E, 0xFE, 0xDE, 0x1E, 0x5E, 0x7E, 0x3E, 0x82, 0x62, 0xF4,
      0x54, 0x44}


def op_len(rom, p):
    b = rom[p]
    if b in L1:
        return 1
    if b in L4:
        return 4
    if b in IMM:
        return 3
    if b in L3:
        return 3
    if b in (0xC2, 0xE2):
        return 2
    return 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('addr')
    ap.add_argument('--count', type=int, default=60)
    a = ap.parse_args()
    rom = open(ROM, 'rb').read()
    p = off(int(a.addr, 16))
    for _ in range(a.count):
        op = rom[p]
        if op & 1 or op // 2 > 0x28:
            print('%06X  %02X  ?? (not an opcode)' % (p, op))
            return
        h = rom[off(0xC1871A) + op] | rom[off(0xC1871A) + op + 1] << 8
        sizes = handler_args(rom, h)
        q = p + 1
        args = []
        for s in sizes:
            v = rom[q] if s == 1 else rom[q] | rom[q + 1] << 8
            args.append('%0*X' % (s * 2, v))
            q += s
        print('%06X  %02X  h=%04X  %s' % (p, op, h, ' '.join(args)))
        if op == 0:
            return
        p = q


if __name__ == '__main__':
    sys.exit(main())
