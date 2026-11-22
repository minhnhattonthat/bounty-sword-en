"""Static sweep of only the graphics-like 4 KB blocks that tools/gfx_map.py found, each at its own tile phase.

    python -X utf8 tools/gfx_map.py > work/sweep/gfxmap.txt
    python -X utf8 tools/gfx_sweep_map.py work/sweep/gfxmap.txt OUTDIR [--per 8] [--zoom 2]

Each 4 KB block = 4 rows of 64 2bpp tiles, labelled `offset+phase`; PER blocks per sheet (8 = 32 KB, 1112x512 at
zoom 2, where kana and kanji read clearly). Prints every block it renders and every non-GFX run it leaves out, so
the skip list is explicit (text, fill and code-like blocks: see gfx_map.py).
"""
import argparse
import os
import re
from PIL import Image, ImageDraw

ROM = open('rom/Bounty Sword (Japan).sfc', 'rb').read()


def tile(t):
    return [[((t[y * 2] >> (7 - x)) & 1) | (((t[y * 2 + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('out')
    ap.add_argument('--per', type=int, default=8)
    ap.add_argument('--zoom', type=int, default=2)
    a = ap.parse_args()
    blocks = []
    for l in open(a.map):
        m = re.match(r'(\w{6})-(\w{6}) (\S+)', l)
        if not m:
            continue
        s, e, c = int(m[1], 16), int(m[2], 16), m[3]
        if c.startswith('GFX+'):
            p = int(c[4:], 16)
            blocks += [(o, p) for o in range(s, e, 0x1000)]
        else:
            print('skip %06X-%06X %s' % (s, e, c))
    os.makedirs(a.out, exist_ok=True)
    pal = [255, 170, 85, 0]
    margin = 52
    for k in range(0, len(blocks), a.per):
        grp = blocks[k:k + a.per]
        img = Image.new('L', (margin + 64 * 8, len(grp) * 32), 255)
        d = ImageDraw.Draw(img)
        px = img.load()
        for bi, (o, p) in enumerate(grp):
            d.text((1, bi * 32 + 1), '%06X' % o, fill=0)
            d.text((1, bi * 32 + 11), '+%X' % p, fill=0)
            for t in range(256):
                src = o + p + t * 16
                if src + 16 > len(ROM):
                    break
                tx, ty = margin + (t % 64) * 8, bi * 32 + (t // 64) * 8
                for y, row in enumerate(tile(ROM[src:src + 16])):
                    for x, v in enumerate(row):
                        px[tx + x, ty + y] = pal[v]
        img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
        name = os.path.join(a.out, 'map_%06X.png' % grp[0][0])
        img.save(name)
        print(name, ' '.join('%06X' % o for o, p in grp))
    print('%d blocks, %d sheets' % (len(blocks), (len(blocks) + a.per - 1) // a.per))


if __name__ == '__main__':
    main()
