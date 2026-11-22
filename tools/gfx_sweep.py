"""Static graphics sweep: render the whole ROM as SNES 2bpp or 4bpp tiles into numbered sheets with offset labels.

    python -X utf8 tools/gfx_sweep.py OUTDIR [--bpp 2|4] [--cols 128] [--rows 128] [--from HEX] [--to HEX] [--zoom N]

Pick ranges with tools/gfx_map.py (GFX-classified 4 KB blocks); 2bpp, 64 cols x 32 rows, zoom 2 reads well.

Each sheet row is labelled with the file offset of its first tile. Nothing is skipped: every byte of the range
lands on some sheet (the last one may be short). Used for the phase-1 graphics-text survey (docs/re/graphics.md).
"""
import argparse
import os
from PIL import Image, ImageDraw

ROM = 'rom/Bounty Sword (Japan).sfc'


def decode(t, bpp):
    rows = []
    for y in range(8):
        p = [t[y * 2], t[y * 2 + 1]]
        if bpp == 4:
            p += [t[16 + y * 2], t[16 + y * 2 + 1]]
        rows.append([sum(((p[k] >> (7 - x)) & 1) << k for k in range(bpp)) for x in range(8)])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--bpp', type=int, default=2, choices=(2, 4))
    ap.add_argument('--cols', type=int, default=128)
    ap.add_argument('--rows', type=int, default=128)
    ap.add_argument('--from', dest='lo', default='0')
    ap.add_argument('--to', dest='hi', default=None)
    ap.add_argument('--zoom', type=int, default=1)
    a = ap.parse_args()
    rom = open(ROM, 'rb').read()
    lo = int(a.lo, 16); hi = int(a.hi, 16) if a.hi else len(rom)
    ts = 8 * a.bpp
    per = a.cols * a.rows * ts
    os.makedirs(a.out, exist_ok=True)
    levels = 1 << a.bpp
    pal = [int(255 * (levels - 1 - i) / (levels - 1)) for i in range(levels)]
    margin = 44
    n = 0
    for base in range(lo, hi, per):
        img = Image.new('L', (margin + a.cols * 8, a.rows * 8), 255)
        d = ImageDraw.Draw(img)
        px = img.load()
        for r in range(a.rows):
            off = base + r * a.cols * ts
            if off >= hi:
                break
            if r % 4 == 0:
                d.text((1, r * 8 - 1), '%06X' % off, fill=0)
            for c in range(a.cols):
                o = off + c * ts
                if o + ts > hi:
                    break
                for y, row in enumerate(decode(rom[o:o + ts], a.bpp)):
                    for x, v in enumerate(row):
                        px[margin + c * 8 + x, r * 8 + y] = pal[v]
        name = os.path.join(a.out, 'sweep%d_%06X.png' % (a.bpp, base))
        if a.zoom > 1:
            img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
        img.save(name)
        print(name)
        n += 1
    print('%d sheets, %06X-%06X, nothing skipped' % (n, lo, hi))


if __name__ == '__main__':
    main()
