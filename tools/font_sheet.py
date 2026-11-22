"""Render the 8x16 main font (bank $EB) as a labelled sheet: python -X utf8 tools/font_sheet.py OUT.png [first_code] [count] [--zoom N]

Glyph layout (docs/re/text.md): 16 codes per row; for row r the top 8x8 2bpp tiles of the 16 codes sit at
FONT + r*0x200 + (code&15)*16, the bottom tiles 0x100 after them.
"""
import sys
from PIL import Image, ImageDraw

ROM = 'rom/Bounty Sword (Japan).sfc'
FONT = 0x2B2D8C  # file offset of $EB:2D8C (HiROM)
PAL = [(255, 255, 255), (0, 0, 0), (120, 120, 120), (200, 60, 60)]


def tile2bpp(data):
    px = []
    for y in range(8):
        lo, hi = data[y * 2], data[y * 2 + 1]
        px.append([((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1) for x in range(8)])
    return px


def glyph(rom, code):
    base = FONT + (code & 0xFFF0) * 32 + (code & 15) * 16
    return tile2bpp(rom[base:base + 16]) + tile2bpp(rom[base + 0x100:base + 0x110])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    zoom = 3
    if '--zoom' in sys.argv:
        zoom = int(sys.argv[sys.argv.index('--zoom') + 1]); args.remove(str(zoom))
    out = args[0]
    first = int(args[1], 16) if len(args) > 1 else 0
    count = int(args[2], 16) if len(args) > 2 else 0x400
    rom = open(ROM, 'rb').read()
    cols = 16
    cw, chh = 8 * zoom + 34, 16 * zoom + 4
    rows = (count + cols - 1) // cols
    img = Image.new('RGB', (cols * cw, rows * chh), (230, 230, 255))
    d = ImageDraw.Draw(img)
    for i in range(count):
        code = first + i
        gx, gy = (i % cols) * cw, (i // cols) * chh
        d.text((gx + 1, gy + 2), '%03X' % code, fill=(0, 0, 160))
        g = glyph(rom, code)
        for y in range(16):
            for x in range(8):
                d.rectangle([gx + 26 + x * zoom, gy + 2 + y * zoom, gx + 26 + x * zoom + zoom - 1,
                             gy + 2 + y * zoom + zoom - 1], fill=PAL[g[y][x]])
    img.save(out)


if __name__ == '__main__':
    main()
