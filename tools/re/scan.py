"""Find regions of 16-bit text (kana codes 0x111-0x1C6) in the ROM."""
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
N = len(rom)


def kana(c):
    return 0x111 <= c <= 0x1C6


hits = []  # word offsets that are kana and have a kana word within the next 2 words
for par in (0, 1):
    for o in range(par, N - 6, 2):
        c = rom[o] | rom[o + 1] << 8
        if kana(c):
            c2 = rom[o + 2] | rom[o + 3] << 8
            c3 = rom[o + 4] | rom[o + 5] << 8
            if kana(c2) and kana(c3):
                hits.append(o)
hits.sort()
# cluster
regions = []
for h in hits:
    if regions and h - regions[-1][1] < 0x200:
        regions[-1][1] = h; regions[-1][2] += 1
    else:
        regions.append([h, h, 1])
for a, b, n in regions:
    if n >= 3:
        print('%06X-%06X  %6d bytes  %5d hits  parity %d' % (a, b, b - a, n, a & 1))
