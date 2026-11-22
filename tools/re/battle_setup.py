"""Static parser for the battle-setup records (pointer table C4:2A39, parser C0:A3AE, unit entry C0:A496).

    python -X utf8 tools/re/battle_setup.py [ROM] [--names] [--tsv]

Record = count byte, then `count` unit entries (C0:A3AE reads the same list twice, once per side). Unit entry,
offsets from its start (C0:A496..A69D, handlers C0:A69E / C0:A72B tables):
  +0 word, +2 word, +4 3 bytes (C0:A77F lookup), +7 byte, +8 byte, +9 slot byte ($24),
  +10 word: 0 = no name (2 bytes); else a 6-word name override copied to $1132 + 12*slot (12 bytes)
  then byte b (b != FF: one more byte), byte c (c == FF: entry ends), byte d -> handler table 1 argument bytes,
  byte, byte e -> handler table 2 argument bytes, byte, byte f (FF: one more byte; else up to 8 bytes ending
  at the first byte >= 0x80, which is consumed).
`--names` lists the name overrides (file offset, JP); `--tsv` prints default_names.tsv rows for them.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

TABLE = 0x042A39          # C4:2A39, 3-byte pointers
COUNT = 263
T1_ARGS = {1: 0, 2: 0, 3: 2, 4: 8, 5: 1, 6: 0, 7: 1, 8: 4}     # JSR ($A69E,x): bytes each handler reads
T2_ARGS = {1: 4, 2: 0, 3: 0, 4: 1}                               # JSR ($A72B,x)


def hirom(addr):
    return (addr & 0x3FFFFF) if addr >= 0xC00000 else addr & 0x3FFFFF


def parse_entry(rom, p):
    """Returns (end offset, name offset or None, slot)."""
    slot = rom[p + 9]
    name = None
    q = p + 10
    if rom[q] | rom[q + 1] << 8:
        name = q
        q += 12
    else:
        q += 2
    b = rom[q]; q += 1
    if b != 0xFF:
        q += 1
    c = rom[q]; q += 1
    if c == 0xFF:
        return q, name, slot
    d = rom[q]; q += 1
    if d not in T1_ARGS:
        raise ValueError(f"entry {p:06X}: handler 1 index {d}")
    q += T1_ARGS[d]
    q += 1
    e = rom[q]; q += 1
    if e not in T2_ARGS:
        raise ValueError(f"entry {p:06X}: handler 2 index {e}")
    q += T2_ARGS[e]
    q += 1
    if rom[q] == 0xFF:
        return q + 2, name, slot
    for _ in range(8):
        v = rom[q]; q += 1
        if v >= 0x80:
            break
    return q, name, slot


def records(rom):
    """[(index, record offset, end, [(entry offset, name offset or None, slot)])] for every nonzero pointer."""
    out = []
    for i in range(COUNT):
        t = TABLE + 3 * i
        ptr = rom[t] | rom[t + 1] << 8 | rom[t + 2] << 16
        if not ptr:
            continue
        p = hirom(ptr)
        n = rom[p]
        q, ents = p + 1, []
        for _ in range(n):
            end, name, slot = parse_entry(rom, q)
            ents.append((q, name, slot))
            q = end
        out.append((i, p, q, ents))
    return out


def name_fields(rom):
    """{name offset: [record indices]} of every name override."""
    seen = {}
    for i, _, _, ents in records(rom):
        for _, name, _ in ents:
            if name is not None:
                seen.setdefault(name, []).append(i)
    return seen


def main(argv):
    rom_path = next((a for a in argv if not a.startswith("--")), str(ROOT / "rom" / "Bounty Sword (Japan).sfc"))
    rom = Path(rom_path).read_bytes()
    recs = records(rom)
    from script_text import TextCodec
    codec = TextCodec(False)
    if "--names" in argv or "--tsv" in argv:
        for off, idx in sorted(name_fields(rom).items()):
            words = [rom[off + 2 * k] | rom[off + 2 * k + 1] << 8 for k in range(6)]
            while words and not words[-1]:
                words.pop()
            jp = codec.decode(words)
            if "--tsv" in argv:
                print(f"{off:X}\t6\t{jp}\t\tbattle-setup name override, scenarios {','.join(map(str, idx))}")
            else:
                print(f"{off:06X} {jp} {idx}")
        return 0
    # Layout report: records should abut (each ends where some other record or table starts).
    starts = sorted(p for _, p, _, _ in recs)
    gaps = 0
    for i, p, q, ents in recs:
        nxt = next((s for s in starts if s >= q), None)
        if nxt is not None and nxt != q and nxt - q < 0x40:
            gaps += 1
            print(f"record {i} {p:06X}-{q:06X}: next record at {nxt:06X} (gap {nxt - q})")
    print(f"{len(recs)} records, {sum(len(e) for *_, e in recs)} entries, "
          f"{sum(1 for *_, e in recs for x in e if x[1] is not None)} name overrides, {gaps} small gaps")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
