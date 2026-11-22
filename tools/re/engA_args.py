import re
r = open('rom/Bounty Sword (Japan).sfc', 'rb').read()
tab = []
for i in range(0x32):
    e = r[0x24A67 + 4 * i:0x24A67 + 4 * i + 4]
    a = e[0] | e[1] << 8
    if e[2] == 0xC2:
        tab.append((a, i))
tab.sort()
L = []
for l in open('work/re/engA/all.txt', encoding='utf8'):
    try:
        L.append((int(l[3:7], 16), l[30:].rstrip()))
    except ValueError:
        pass
for k, (s, op) in enumerate(tab):
    e = tab[k + 1][0] if k + 1 < len(tab) else s + 0x40
    body = [(a, t) for a, t in L if s <= a < e]
    reads = sum('[$48],y' in t and t.startswith('LDA') for a, t in body)
    adv = []
    for j, (a, t) in enumerate(body):
        if 'STA $7E3727' in t:
            prev = [x[1] for x in body[max(0, j - 4):j]]
            adv.append('/'.join(p.replace(' ', '') for p in prev))
    other = [t for a, t in body if re.match(r'(JMP|JML|JSR|JSL) ', t)]
    print('FF%02X C2:%04X len=%d reads=%d' % (op, s, e - s, reads))
    for x in adv:
        print('    adv:', x)
    print('    calls:', ' '.join(sorted(set(o.split(';')[0].split()[1] for o in other))))
