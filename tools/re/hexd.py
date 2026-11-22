import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
a = int(sys.argv[1], 16); n = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100
w = int(sys.argv[3]) if len(sys.argv) > 3 else 16
for o in range(a, a + n, w):
    print('%06X: %s' % (o, ' '.join('%02x' % b for b in rom[o:o + w])))
