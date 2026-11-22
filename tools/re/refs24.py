"""Find 24-bit pointers (HiROM $C0-$EF) whose target falls in a file range.

python tools/re/refs24.py START END [START END ...]   (hex file offsets)
Prints, per range, the hit count and where the pointers sit, clustered by 4 KB page.
"""
import sys
from collections import Counter

ROM = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
a = [int(x, 16) for x in sys.argv[1:]]
for s, e in zip(a[::2], a[1::2]):
    bank = 0xC0 | (s >> 16)
    lo, hi = s & 0xFFFF, (e & 0xFFFF) if (e >> 16) == (s >> 16) else 0xFFFF
    hits = [i for i in range(len(ROM) - 2) if ROM[i + 2] == bank and lo <= (ROM[i] | ROM[i + 1] << 8) < hi]
    pages = Counter(h >> 12 for h in hits)
    print('%06X-%06X: %d hits; pages %s' % (s, e, len(hits), ' '.join('%03X:%d' % kv for kv in sorted(pages.items()))))
    print('   first:', ' '.join('%06X' % h for h in hits[:16]))
