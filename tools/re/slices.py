"""Which cells of each C1 window string a screen shows (the slice table for translators).

A C1 window string is drawn one 8x16 cell per word into tile slots (`$7E:A000`, DMA'd to VRAM word $1000), and the
screen's tilemap shows slices of those slots. Slot n = tile 0x100 + (n // 16) * 32 + n % 16 (top half; bottom half
+16) relative to a 4bpp BG whose character base is VRAM word 0.

Input: run dirs from warps with the C1 run logger and the VRAM dumper (C1RUN34/40 = the JML targets at file 0x018E90
and 0x018F13 of the build being toured), e.g.

    python -X utf8 tools/debug/warp_all.py build/bounty_marker.sfc --only camp,camp_config,... --jobs 6
        --out work/qa/sl --script tools/lua/c1runs.lua --var C1RUN34=0xFF03DA --var C1RUN40=0xFF03E5
        --script $SKILL/scripts/lua/probes/ppudump.lua --var DUMP_EVERY=30
    python -X utf8 tools/re/slices.py work/qa/sl/* --tsv docs/re/slices.tsv

For each run dir it takes the last VRAM dump, replays the logged runs up to that frame (last writer wins per slot)
and prints every horizontal tilemap run of consecutive slots, split at string boundaries:
scene, string id (file offset; RAM pointers as `RAM:xxxxxx`), first cell, cells, screen column, row, layer.
"""
import argparse
import glob
import os
import re
import sys

SLOT_TILE0 = 0x100  # VRAM word $1000 / 16 words per 4bpp tile
RUN_RE = re.compile(r"f(\d+) sl-?\d+ run(\d\d) slot=([0-9A-F]{4}) n=(\d+) ptr=([0-9A-F]{6})")


def slot_of_tile(idx):
    rel = idx - SLOT_TILE0
    if rel < 0 or (rel // 16) % 2:  # odd 16-tile rows are bottom halves
        return None
    return (rel // 32) * 16 + rel % 16


def ppu_regs(path):
    regs = {}
    for line in open(path, encoding='utf8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            regs[k] = v
    return regs


def slot_owners(log, upto, max_age):
    """Slot -> (string id, cell) from the runs logged in (upto - max_age, upto]: older runs belong to screens
    that are gone, and their slot tiles in VRAM have since been overwritten by other graphics."""
    owners = {}
    for line in open(log, encoding='utf8', errors='replace'):
        m = RUN_RE.search(line)
        if not m or not upto - max_age < int(m.group(1)) <= upto:
            continue
        slot, n, ptr = int(m.group(3), 16), int(m.group(4)), int(m.group(5), 16)
        sid = '%06X' % (ptr & 0x3FFFFF) if ptr >= 0xC00000 else 'RAM:%06X' % ptr
        for i in range(n):
            owners[slot + i] = (sid, i)
    return owners


def scan(run, max_age=900):
    dumps = sorted(glob.glob(os.path.join(run, 'ppu_*.vram.bin')))
    if not dumps:
        return []
    vram_path = dumps[-1]
    frame = int(re.search(r'ppu_(\d+)', vram_path).group(1))
    vram = open(vram_path, 'rb').read()
    regs = ppu_regs(vram_path.replace('.vram.bin', '.ppu.txt'))
    owners = slot_owners(os.path.join(run, 'log.txt'), frame, max_age)
    word = lambda a: vram[2 * (a & 0x7FFF)] | vram[2 * (a & 0x7FFF) + 1] << 8
    scene = os.path.basename(os.path.normpath(run))
    rows = []
    for layer in (0, 1):  # BG1, BG2 (4bpp in modes 0-1 use the same slot tiles only with chr base 0)
        if int(regs.get('ppu.layers[%d].chrAddress' % layer, -1)) != 0:
            continue
        tm = int(regs['ppu.layers[%d].tilemapAddress' % layer])  # first 32x32 screen (scroll 0 on menus)
        for y in range(28):
            cells = []
            for x in range(32):
                t = word(tm + y * 32 + x)
                s = slot_of_tile(t & 0x3FF)
                cells.append(owners.get(s) if s is not None else None)
            x = 0
            while x < 32:
                if cells[x] is None:
                    x += 1
                    continue
                sid, start = cells[x]
                n = 1
                while x + n < 32 and cells[x + n] == (sid, start + n):
                    n += 1
                rows.append((scene, sid, start, n, x, y, 'BG%d' % (layer + 1)))
                x += n
    # one row per distinct slice (menus repeat a slice on several lines)
    seen, out = set(), []
    for r in rows:
        if r[1:4] not in seen:
            seen.add(r[1:4])
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--tsv', help='write the table here instead of stdout')
    ap.add_argument('--max-age', type=int, default=900, help='ignore runs this many frames before the dump')
    a = ap.parse_args()
    out = []
    for run in a.runs:
        out += scan(run, a.max_age)
    head = 'scene\tstring\tfirst_cell\tcells\tcol\trow\tlayer'
    lines = [head] + ['\t'.join(str(v) for v in r) for r in out]
    if a.tsv:
        with open(a.tsv, 'w', encoding='utf8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
        print('%s: %d slices' % (a.tsv, len(out)))
    else:
        sys.stdout.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
