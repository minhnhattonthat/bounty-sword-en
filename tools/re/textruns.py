"""List runs of 16-bit text in the ROM (both parities), excluding the master-dialogue blocks.

A word is texty if it is < 0x500 (char or 0000) or 0xFF00-0xFF31 (control). A run needs >= MINK kana words
and >= 1 kana per 4 words. Prints start-end, words, kana count and a sample.
python -X utf8 tools/re/textruns.py [MINK] > out.txt
"""
import sys
sys.path.insert(0, 'tools/re')
from words import ROM, ch, msg_off, COUNT

MINK = int(sys.argv[1]) if len(sys.argv) > 1 else 6
N = len(ROM)
master = sorted(set(msg_off(i) for i in range(COUNT)))


def texty(c):
    return c < 0x500 or 0xFF00 <= c <= 0xFF31 or c == 0xFFFF


def kana(c):
    return 0x111 <= c <= 0x1C6


def in_master(o):
    import bisect
    i = bisect.bisect_right(master, o) - 1
    return i >= 0 and o - master[i] < 0x600


out = []
for par in (0, 1):
    o = par
    while o < N - 1:
        s = o
        k = 0
        n = 0
        while o < N - 1:
            c = ROM[o] | ROM[o + 1] << 8
            if not texty(c):
                break
            k += kana(c)
            n += 1
            o += 2
        if k >= MINK and k * 4 >= n and not in_master(s):
            # trim leading/trailing zeros
            out.append((s, o, n, k))
        o += 2
out.sort()
for s, e, n, k in out:
    w = [ROM[x] | ROM[x + 1] << 8 for x in range(s, min(e, s + 60), 2)]
    print('%06X-%06X %5d w %4d k  %s' % (s, e, n, k, ''.join(ch(x) for x in w)[:90]))
