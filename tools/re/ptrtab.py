"""Walk a 24-bit pointer table backward and forward from a known entry while entries look like HiROM text pointers."""
import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
at = int(sys.argv[1], 16)


def ok(o):
    v = rom[o] | rom[o + 1] << 8 | rom[o + 2] << 16
    return 0xC00000 <= v <= 0xEFFFFF, v


s = at
while ok(s - 3)[0]:
    s -= 3
e = at
while ok(e)[0]:
    e += 3
print('table %06X-%06X  %d entries' % (s, e, (e - s) // 3))
vals = [ok(o)[1] for o in range(s, e, 3)]
print(' '.join('%06X' % v for v in vals[:400]))
