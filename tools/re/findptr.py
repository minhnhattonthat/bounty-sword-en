import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
for t in sys.argv[1:]:
    off = int(t, 16)
    cpu = 0xC00000 | off
    for name, pat in (('24', cpu.to_bytes(3, 'little')), ('16', (cpu & 0xFFFF).to_bytes(2, 'little'))):
        hits = []
        i = rom.find(pat)
        while i >= 0 and len(hits) < 30:
            hits.append('%06X' % i); i = rom.find(pat, i + 1)
        print(t, name, len(hits), ' '.join(hits))
