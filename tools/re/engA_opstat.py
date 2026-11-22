import sys
from collections import Counter, defaultdict
sys.path.insert(0, 'tools/re')
from words import ROM, msg_off, ch, COUNT

offs = sorted(set(msg_off(i) for i in range(COUNT)))
cnt = Counter()
ctx = defaultdict(list)
ends = Counter()
for k, o in enumerate(offs):
    e = offs[k + 1] if k + 1 < len(offs) and offs[k + 1] - o < 0x2000 else o + 0x400
    w = [ROM[x] | ROM[x + 1] << 8 for x in range(o, e, 2)]
    ends[' '.join('%04X' % x for x in w[-2:])] += 1
    for i, c in enumerate(w):
        if c >= 0xFF00 and c != 0xFFFF:
            cnt[c] += 1
            if len(ctx[c]) < 6:
                ctx[c].append('%06X ' % (o + 2 * i) + ''.join(ch(x) for x in w[max(0, i - 3):i + 6]))
for c, n in sorted(cnt.items()):
    print('%04X %6d' % (c, n))
    for s in ctx[c]:
        print('      ', s)
print('message tails:', ends.most_common(8))
