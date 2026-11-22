"""Dump 16-bit LE script words with kana decoding.

python -X utf8 tools/re/words.py FILEOFF [NWORDS]       (hex offset)
python -X utf8 tools/re/words.py --msg N [NWORDS]       (master table entry N)
Control words print as <FFxx>, unknown characters as {xxx}.
"""
import sys

ROM = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
HIRA = ''.join(chr(c) for c in range(0x3041, 0x3094))
KATA = ''.join(chr(c) for c in range(0x30A1, 0x30F7))
SYM = {0x03: '。', 0x04: '、', 0x09: '？', 0x0A: '！', 0x1D: 'ー', 0x36: '「', 0x37: '」', 0x400: '‥'}
TABLE = 0x26D772
COUNT = 2333


def ch(c):
    if c >= 0xFF00:
        return '<%04X>' % c
    if c == 0:
        return '_'
    if c in SYM:
        return SYM[c]
    if 0x111 <= c < 0x111 + len(HIRA):
        return HIRA[c - 0x111]
    if 0x171 <= c < 0x171 + len(KATA):
        return KATA[c - 0x171]
    if 0xC0 <= c <= 0xC9:
        return str(c - 0xC0)
    if 0xD1 <= c <= 0xEA:
        return chr(ord('A') + c - 0xD1)
    return '{%X}' % c


def msg_off(n):
    p = TABLE + 3 * n
    return (ROM[p] | ROM[p + 1] << 8 | ROM[p + 2] << 16) & 0x3FFFFF


def main():
    a = sys.argv[1:]
    if a[0] == '--msg':
        off = msg_off(int(a[1], 0))
        a = a[1:]
    else:
        off = int(a[0], 16)
    n = int(a[1], 0) if len(a) > 1 else 64
    print('%06X: ' % off + ''.join(ch(ROM[o] | ROM[o + 1] << 8) for o in range(off, off + 2 * n, 2)))


if __name__ == '__main__':
    main()
