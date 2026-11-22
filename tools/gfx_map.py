"""Classify each 4 KB block of the ROM as graphics-like or not, for the phase-1 static sweep.

    python -X utf8 tools/gfx_map.py [--thr 0.72]

Score = mean agreement of neighbouring pixel rows inside 8x8 tiles (bitplane 0, 2bpp/4bpp layouts both start
with rows of plane 0/1 interleaved). Random code/data scores ~0.5, tile graphics ~0.75-0.95. Fill (all 00/FF)
and blocks that are mostly 16-bit text words are reported as such. GFX+P = graphics whose tiles start at byte
phase P (best score over even phases 0-14). Prints one line per run of same-class blocks.
"""
import argparse

ROM = open('rom/Bounty Sword (Japan).sfc', 'rb').read()


def score(b):
    agree = 0
    n = 0
    for t in range(0, len(b) - 15, 16):
        for y in range(7):
            a, c = b[t + 2 * y], b[t + 2 * y + 2]
            agree += 8 - bin(a ^ c).count('1')
            n += 8
    return agree / n


def textish(b):
    best = 0
    for par in (0, 1):  # text blocks sit at odd offsets too (0x280F25)
        w = [b[i] | b[i + 1] << 8 for i in range(par, len(b) - 1, 2)]
        best = max(best, sum(1 for x in w if x < 0x500 or x >= 0xFF00) / len(w))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--thr', type=float, default=0.72)
    a = ap.parse_args()
    runs = []
    for o in range(0, len(ROM), 0x1000):
        b = ROM[o:o + 0x1000]
        if b.count(b[0]) == len(b):
            cls = 'fill'
        elif textish(b) > 0.8:
            cls = 'text/words'
        else:
            # tile phase: graphics need not start 16-byte aligned (the chapter-card glyphs sit at 0x18449A)
            sc = [(score(ROM[o + p:o + p + 0x1000]), p) for p in range(0, 16, 2)]
            s, p = max(sc)
            cls = 'GFX+%X' % p if s >= a.thr else 'other'
        if runs and runs[-1][2] == cls:
            runs[-1][1] = o + 0x1000
        else:
            runs.append([o, o + 0x1000, cls])
    for s, e, c in runs:
        print('%06X-%06X %-10s %3d KB' % (s, e, c, (e - s) >> 10))
    print('GFX total: %d KB' % (sum(e - s for s, e, c in runs if c.startswith('GFX')) >> 10))


if __name__ == '__main__':
    main()
