"""byte_scripts.py: engine A side scripts read at byte level (docs/re/text.md §Engine A, docs/re/jp_left.md).

Some engine A scripts use the opcodes with byte-sized arguments (FF25/FF27/FF29/FF2A: a 24-bit RAM address; FF26: a
24-bit address and a 24-bit jump target), so their text flips between the even and odd word phase and the word
layout of rom_text.REGIONS can't hold them. Each table here is tokenised byte by byte instead:

- text as in the side tables (`script_text.TextCodec(False)`): characters, `[hhhh]` words, `{FFxx}` / `{FFxx:hhhh}`;
- `{FF25:7F72AD}` etc.: an opcode with a 3-byte address argument (big-endian, as the address reads);
- `{FF26:7F72AD>05E997}` / `{FF26:7F72B5>@1}`: "if the byte at the address is 0, jump": the target is an entry id
  or a label `{@1}` in the same entry. The handler (C2:6360) jumps by a 16-bit offset from the script base `$48`,
  so a jump never leaves the bank: the build keeps every unit (below) whole in one bank.

Entries end after FF00 or FF03 (FF03 waits and runs on into the next entry). A **unit** is a run of entries up to an
FF00 that no jump leaves. A unit whose text fits its slot is written in place (the old bytes after it stay); a longer
one goes to BYTE_AREA in the expanded ROM. Every entry with known callers (`refs`: 24-bit operands, filtered by the
table's caller form) gets its pointers rewritten to wherever it lands, so a relocated unit needs a caller at its
first entry.

    from byte_scripts import extract, layout
    files = extract(rom)                    # {"battle_prompts.json": [entries], ...}
    writes, sites = layout(rom, files, "en")  # [(file offset, bytes)], [(start, end, what)] for romdiff
"""
import re

from rom_text import ROM_EXPANDED, to_cpu, to_file, word
from script_text import ENGINE_A_ARGS, TextCodec, pointer_index

# Engine A argument bytes per opcode (handlers C2:4B2F.., tools/re/engA_args.py; FF25-FF2A read 2026-11-23).
ARG_BYTES = {0xFF05: 2, 0xFF06: 2, 0xFF09: 2, 0xFF0A: 2, 0xFF0B: 2, 0xFF0C: 2, 0xFF14: 2,
             0xFF25: 3, 0xFF26: 6, 0xFF27: 3, 0xFF29: 3, 0xFF2A: 3}
UNSUPPORTED = {0xFF0F, 0xFF10, 0xFF2D}       # conditional argument counts: not in these tables
ENDS = {0xFF00, 0xFF03}
JUMP = 0xFF26

# name -> (segments [(start, end)], caller filter). A caller is a 24-bit operand equal to an entry's CPU address;
# `ops`: the byte before it must be one of these event-script opcodes; `area`: the operand must lie in this range.
BYTE_TABLES = {
    # C5 event-script `2E ptr24` calls (0x06CCA7 calls 05E8A2). Starts at the first script; the word 0x011E at
    # 0x05E8A0 is the tail of the data before it. Ends after the last FF00 (0x05EFFF); the tavern roster lists,
    # job offers and the treasure-chest lines use FF25-FF29 and run in the odd word phase.
    "battle_prompts": ([(0x05E8A2, 0x05F001)], {"ops": {0x2E}}),
    # Map-command prompts (target / area / move), called through 3-byte pointer lists in bank C0 (C0:F1CE..F41B)
    # and the pointer table at C0:FD9B.
    "target_prompts": ([(0x05A52E, 0x05A582)], {"area": (0x00F000, 0x010000)}),
    # Level-up stat lines between code in bank DA, each called by a C0-style op list `43 ptr24` just before it.
    "level_up": ([(0x1AD456, 0x1AD473), (0x1AD4D1, 0x1AD4EE), (0x1AD54C, 0x1AD567), (0x1AD5C5, 0x1AD5E0),
                  (0x1AD641, 0x1AD65C), (0x1AD6BD, 0x1AD6D8), (0x1AD739, 0x1AD758), (0x1AD7A1, 0x1AD7C0)],
                 {"ops": {0x43}}),
    # The level-up talk in bank C4 (the guide's portrait box after a map: level, stats, spells and skills learnt,
    # item found), called by `03 ptr24` from the C4 event script (0414C9 by `03 C914C4` at 0x0412A0) and chained by
    # FF26 skips. Cut out of system_prompts: it was dumped word by word there, out of phase after its first FF25,
    # so it stayed `data` and Japanese in game (user screenshots 2026-11-23, rom/ss).
    "level_up_msgs": ([(0x0414C9, 0x041865)], {"ops": {0x03}}),
}
# Relocated units: the last bank of the expanded text area (rom_text.EXPANDED_TEXT stops below it).
BYTE_AREA = (0x3E0000, 0x3F0000)
ADDR = {}    # entry id -> file offset of its first byte in the last layout() (build/strings.tsv)

TOKEN = re.compile(r"\{[^}]*\}")
ADDR_OP = re.compile(r"\{(FF2[579A]):([0-9A-F]{6})\}$")
JUMP_OP = re.compile(r"\{FF26:([0-9A-F]{6})>(@\d+|[0-9A-F]{6})\}$")
LABEL = re.compile(r"\{(@\d+)\}$")


def _codec():
    return TextCodec(False, args=ENGINE_A_ARGS)


def tokens(rom, start, end):
    """[(offset, opcode or None, raw bytes)] for [start, end); a word that isn't an opcode has opcode None."""
    out, p = [], start
    while p < end:
        w = word(rom, p)
        if w in UNSUPPORTED:
            raise ValueError(f"engine A opcode {w:04X} at {p:06X}: conditional arguments, not handled")
        n = 2 + (ARG_BYTES.get(w, 0) if w >= 0xFF00 else 0)
        if p + n > end:
            raise ValueError(f"token at {p:06X} runs past {end:06X}")
        out.append((p, w if w >= 0xFF00 else None, rom[p:p + n]))
        p += n
    return out


def split_entries(toks):
    """Token lists, each ending after FF00 or FF03."""
    out, cur = [], []
    for t in toks:
        cur.append(t)
        if t[1] in ENDS:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _target(raw):
    return to_file(raw[5] | raw[6] << 8 | raw[7] << 16)


def decode_entry(toks, ids, codec):
    """One entry's tokens -> text. `ids`: file offsets of every entry start in the table (jump targets by id)."""
    here = {t[0] for t in toks}
    labels = {}
    for off, op, raw in toks:
        if op == JUMP:
            t = _target(raw)
            if t not in ids and t not in labels:
                if t not in here:
                    raise ValueError(f"FF26 at {off:06X} jumps to {t:06X}: not an entry start nor in its entry")
                labels[t] = "@%d" % (len(labels) + 1)
    out = []
    for off, op, raw in toks:
        if off in labels:
            out.append("{%s}" % labels[off])
        if op == JUMP:
            t = _target(raw)
            out.append("{FF26:%02X%02X%02X>%s}" % (raw[4], raw[3], raw[2], labels.get(t) or "%06X" % t))
        elif op is not None and ARG_BYTES.get(op) == 3:
            out.append("{%04X:%02X%02X%02X}" % (op, raw[4], raw[3], raw[2]))
        else:
            out.append(codec.decode([word(raw, i) for i in range(0, len(raw), 2)]))
    return "".join(out)


def callers(rom, name, entry_offsets, ptrs=None):
    """{entry offset: [file offsets of 24-bit operands pointing at it]} by the table's caller filter."""
    ptrs = ptrs if ptrs is not None else pointer_index(rom)
    rule = BYTE_TABLES[name][1]
    out = {}
    for o in entry_offsets:
        refs = ptrs.get(o, [])
        if "ops" in rule:
            refs = [r for r in refs if r > 0 and rom[r - 1] in rule["ops"]]
        if "area" in rule:
            refs = [r for r in refs if rule["area"][0] <= r < rule["area"][1]]
        if refs:
            out[o] = refs
    return out


def extract(rom, ptrs=None):
    """Entries per table file: id, kind text, jp, en "", refs (caller operand offsets)."""
    codec = _codec()
    ptrs = ptrs if ptrs is not None else pointer_index(rom)
    files = {}
    for name, (segs, _) in BYTE_TABLES.items():
        groups = [g for s, e in segs for g in split_entries(tokens(rom, s, e))]
        ids = {g[0][0] for g in groups}
        refs = callers(rom, name, ids, ptrs)
        entries = []
        for g in groups:
            off = g[0][0]
            e = {"id": "%06X" % off, "kind": "text", "jp": decode_entry(g, ids, codec), "en": ""}
            if off in refs:
                e["refs"] = ["%06X" % r for r in refs[off]]
            entries.append(e)
        files[name + ".json"] = entries
    return files


class Piece:
    """An encoded entry: bytes with label positions and FF26 target fields still to fill."""

    def __init__(self, data, labels, jumps):
        self.data, self.labels, self.jumps = data, labels, jumps   # jumps: [(byte index of target, "@1" / id)]


def encode_entry(text, codec):
    data, labels, jumps = bytearray(), {}, []
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            data += b"".join(w.to_bytes(2, "little") for w in codec.encode(text[pos:m.start()]))
        tok = m.group(0)
        if (a := ADDR_OP.match(tok)):
            data += int(a.group(1), 16).to_bytes(2, "little") + int(a.group(2), 16).to_bytes(3, "little")
        elif (j := JUMP_OP.match(tok)):
            data += JUMP.to_bytes(2, "little") + int(j.group(1), 16).to_bytes(3, "little")
            jumps.append((len(data), j.group(2)))
            data += b"\0\0\0"
        elif (lb := LABEL.match(tok)):
            if lb.group(1) in labels:
                raise ValueError(f"label {tok} twice")
            labels[lb.group(1)] = len(data)
        else:
            data += b"".join(w.to_bytes(2, "little") for w in codec.encode(tok))
        pos = m.end()
    if pos < len(text):
        data += b"".join(w.to_bytes(2, "little") for w in codec.encode(text[pos:]))
    missing = [t for _, t in jumps if t.startswith("@") and t not in labels]
    if missing:
        raise ValueError(f"jump to undefined label {missing}")
    return Piece(bytes(data), labels, jumps)


def units(entries, texts):
    """Index runs of entries placed together: up to an entry ending in FF00, extended while a jump in the run
    targets an entry after it."""
    index = {e["id"]: i for i, e in enumerate(entries)}
    out, i = [], 0
    while i < len(entries):
        j, end = i, i
        while True:
            for t in re.findall(r"\{FF26:[0-9A-F]{6}>([0-9A-F]{6})\}", texts[j]):
                if t not in index:
                    raise ValueError(f"{entries[j]['id']}: jump to {t}, not an entry of this table")
                end = max(end, index[t])
            if j >= end and texts[j].endswith("{FF00}") or j == len(entries) - 1:
                break
            j += 1
            end = max(end, j)
        out.append(list(range(i, j + 1)))
        i = j + 1
    return out


def layout(rom, files, field="en"):
    """Bytes to write for every byte table with each entry's `field` text (empty -> jp):
    ([(file offset, bytes)], [(start, end, what)] for the scattered caller rewrites)."""
    codec = _codec()
    writes, sites = [], []
    spill = BYTE_AREA[0]
    ADDR.clear()
    for name, (segs, _) in BYTE_TABLES.items():
        entries = files[name + ".json"]
        seg_of = lambda off: next((s, e) for s, e in segs if s <= off < e)
        pieces = [encode_entry(e.get(field) or e["jp"], codec) for e in entries]
        jp_len = [len(encode_entry(e["jp"], codec).data) for e in entries]
        addr = {}            # entry id -> file offset where it lands
        placed = []          # (unit, base file offset)
        for u in units(entries, [e["jp"] for e in entries]):     # the JP's jumps fix the units

            start = int(entries[u[0]]["id"], 16)
            seg = seg_of(start)
            old = sum(jp_len[i] for i in u)
            new = sum(len(pieces[i].data) for i in u)
            if new <= old and start + old <= seg[1]:
                base = start
            else:
                if not entries[u[0]].get("refs"):
                    raise ValueError(f"{name} {entries[u[0]]['id']}: English is {new - old} bytes longer than the "
                                     "JP and no caller is known, so it must fit in place")
                if (spill >> 16) != ((spill + new - 1) >> 16):
                    spill = (spill + 0xFFFF) & ~0xFFFF
                if spill + new > BYTE_AREA[1]:
                    raise ValueError(f"byte-script area full at {name} {entries[u[0]]['id']}")
                base, spill = spill, spill + new + (new & 1)
            p = base
            for i in u:
                addr[entries[i]["id"]] = p
                p += len(pieces[i].data)
            placed.append((u, base))
        ADDR.update(addr)
        for u, base in placed:
            blob = bytearray()
            for i in u:
                pc, here = pieces[i], addr[entries[i]["id"]]
                data = bytearray(pc.data)
                for at, t in pc.jumps:
                    dest = here + pc.labels[t] if t.startswith("@") else addr[t]
                    if dest >> 16 != base >> 16:
                        raise ValueError(f"{name} {entries[i]['id']}: jump to {dest:06X} leaves bank {base >> 16:02X}")
                    data[at:at + 3] = to_cpu(dest).to_bytes(3, "little")
                blob += data
            writes.append((base, bytes(blob)))
        for e in entries:
            for r in e.get("refs", ()):
                r = int(r, 16)
                writes.append((r, to_cpu(addr[e["id"]]).to_bytes(3, "little")))
                sites.append((r, r + 3, f"caller of {name} {e['id']}"))
    return writes, sites


def put(rom, writes):
    """Apply layout() writes to a bytearray, growing it to ROM_EXPANDED when a unit was relocated."""
    for off, b in writes:
        if off + len(b) > len(rom):
            rom += b"\xff" * (ROM_EXPANDED - len(rom))
        rom[off:off + len(b)] = b
    return rom


def ranges():
    """[(start, end)) of the in-place segments (romdiff allowed ranges)."""
    return [seg for segs, _ in BYTE_TABLES.values() for seg in segs]
