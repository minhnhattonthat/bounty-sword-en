import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
pat = bytes.fromhex(sys.argv[1])
lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else len(rom)
i = rom.find(pat, lo)
while 0 <= i < hi:
    print('%06X  %s' % (i, rom[max(0, i - 16):i + len(pat) + 8].hex(' ')))
    i = rom.find(pat, i + 1)
