import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
HIRA = ''.join(chr(c) for c in range(0x3041, 0x3094))
KATA = ''.join(chr(c) for c in range(0x30A1, 0x30F7))
HB = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x11E


def ch(c):
    if 0x171 <= c < 0x171 + len(KATA):
        return KATA[c - 0x171]
    if HB <= c < HB + len(HIRA):
        return HIRA[c - HB]
    if 0xC0 <= c <= 0xC9:
        return str(c - 0xC0)
    return '{%X}' % c


a = int(sys.argv[1], 16); n = int(sys.argv[2], 16)
out = []
for o in range(a, a + n, 2):
    c = rom[o] | rom[o + 1] << 8
    out.append(ch(c))
    if c == 0:
        out.append('\n')
print(''.join(out))
