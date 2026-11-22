"""Print 24-bit little-endian pointers at a file offset: python tools/re/p24.py FILEOFF COUNT [STRIDE]"""
import sys
sys.path.insert(0, 'tools/re')
from words import ROM, ch

o = int(sys.argv[1], 16)
n = int(sys.argv[2], 0)
st = int(sys.argv[3], 0) if len(sys.argv) > 3 else 3
for i in range(n):
    p = o + i * st
    v = ROM[p] | ROM[p + 1] << 8 | ROM[p + 2] << 16
    t = v & 0x3FFFFF
    s = ''.join(ch(ROM[x] | ROM[x + 1] << 8) for x in range(t, t + 24, 2)) if v >= 0xC00000 else ''
    print('%06X: %06X  %s' % (p, v, s))
