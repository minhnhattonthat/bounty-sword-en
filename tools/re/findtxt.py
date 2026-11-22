import sys
rom = open('rom/Bounty Sword (Japan).sfc', 'rb').read()


def code(ch):
    o = ord(ch)
    if 0x3041 <= o <= 0x3093:
        return 0x111 + o - 0x3041
    if 0x30A1 <= o <= 0x30F6:
        return 0x171 + o - 0x30A1
    raise ValueError(ch)


for w in sys.argv[1:]:
    pat = b''.join(code(c).to_bytes(2, 'little') for c in w)
    i = rom.find(pat); hits = []
    while i >= 0:
        hits.append('%06X' % i); i = rom.find(pat, i + 1)
    print(w, len(hits), ' '.join(hits[:40]))
