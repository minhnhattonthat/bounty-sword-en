"""rom_text.py: unpack and repack every text structure in Bounty Sword (docs/re/text.md).

    from rom_text import unpack, repack
    data = unpack(rom)          # dict: master blocks + slot map, in-place regions
    out = repack(rom, data)     # bytes; with no edits, out == rom (tests/test_identity.py)

Text is kept per 16-bit word, losslessly: a word with a canonical tbl/jp.tbl entry becomes that character, a control
word (>= 0xFF00) becomes `{FFxx}`, any other word (0x0000, unidentified kanji, data) becomes `[XXXX]`. Control-code
arguments are not parsed here; the phase-4 extractor adds that on top of the same layout.

Master dialogue (engine A): a 3-byte pointer table at MASTER_TABLE (lo, hi, bank; 0 = unused slot). A message runs to
the next pointer target; the last message of a block ends after its first 」FFFF that isn't followed by FF18. Repack
writes each block's messages back to back from the block start and rewrites every slot, so a longer or shorter message
moves everything after it; a message that no longer fits its block goes to the expanded ROM (any message may live
anywhere: each has its own pointer, and engine A's skips are relative).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TBL = ROOT / "tbl" / "jp.tbl"

MASTER_TABLE = 0x26D5EF
MASTER_END = 0x26F2C9            # first byte after the last slot: 2,462 slots
# Block starts (file offsets), verified by unpack(): a gap > BLOCK_GAP between two message targets is data, not text.
MASTER_BLOCKS = (0x1E0000, 0x214606, 0x24DB56, 0x257BD4, 0x26F317, 0x271410, 0x280F1B, 0x290400, 0x2A7D44)
BLOCK_GAP = 0x400
# Master messages that no longer fit their block go to the expanded ROM (docs/re/rom.md): file 0x300000-0x3EFFFF
# ($F0-$FE). Bank $FF holds the engine patch (asm/vwf.asm).
ROM_EXPANDED = 0x400000
EXPANDED_TEXT = (0x300000, 0x3F0000)

# Text found outside the master table (docs/re/text.md §Text inventory), repacked in place, same length.
# (name, first byte, end exclusive). Phase 4 replaces these with pointer-aware tables as each reader is confirmed.
REGIONS = (
    ("locations", 0x00CD7B, 0x00D151),
    ("battle_prompts_b", 0x0073AB, 0x007673),
    ("menus", 0x01BFFF, 0x01D3AB),
    ("speakers", 0x025D5D, 0x025F7F),
    ("system_prompts", 0x04136F, 0x0418E3),
    ("unit_records", 0x046CF4, 0x0473B0),
    ("battle_prompts", 0x05E8A0, 0x05EF52),
    ("unit_names", 0x06E3AB, 0x06E627),
    ("unit_titles", 0x08DF4A, 0x08E9D6),
    ("classes", 0x0BF8AE, 0x0C0004),
    ("descriptions", 0x0EE59E, 0x0EFD28),
    ("objectives", 0x18FD06, 0x18FF48),
    ("items", 0x1ADFEF, 0x1AEDB9),
    ("short_strings", 0x1AF349, 0x1AFDC3),
    ("ceremony", 0x1DEBCF, 0x1DF5A3),
)

LBRACKET, RBRACKET, FFFF, FF18 = 0x0036, 0x0037, 0xFFFF, 0xFF18


def word(rom, o):
    return rom[o] | rom[o + 1] << 8


def to_cpu(off):
    """HiROM file offset -> 24-bit CPU address in the $C0-$FF mirror (what the game's pointers hold)."""
    return 0xC00000 | off


def to_file(addr):
    return addr & 0x3FFFFF


class WordCodec:
    """16-bit word <-> text, lossless for every word value."""

    def __init__(self, path=TBL):
        self.dec, self.enc = {}, {}
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            if not line or line.startswith("#"):
                continue
            key, _, val = line.partition("=")
            b = bytes.fromhex(key)
            w = b[0] | b[1] << 8
            if val not in self.enc:      # first code for a character is canonical; later duplicates stay escaped
                self.enc[val] = w
                self.dec[w] = val

    def decode(self, words):
        out = []
        for w in words:
            if w >= 0xFF00:
                out.append("{%04X}" % w)
            elif w in self.dec:
                out.append(self.dec[w])
            else:
                out.append("[%04X]" % w)
        return "".join(out)

    def encode(self, text):
        out, i = [], 0
        while i < len(text):
            c = text[i]
            if c in "{[":
                close = "}" if c == "{" else "]"
                j = text.index(close, i)
                w = int(text[i + 1:j], 16)
                if (c == "{") != (w >= 0xFF00):
                    raise ValueError(f"{text[i:j + 1]} at {i}: braces are for FFxx controls, brackets for other words")
                out.append(w)
                i = j + 1
            elif c in self.enc:
                out.append(self.enc[c])
                i += 1
            else:
                raise ValueError(f"unencodable {c!r} at {i} in {text!r}")
        return out

    def encode_bytes(self, text):
        return b"".join(w.to_bytes(2, "little") for w in self.encode(text))


def words_at(rom, start, end):
    if (end - start) % 2:
        raise ValueError(f"odd length {start:#x}-{end:#x}")
    return [word(rom, o) for o in range(start, end, 2)]


def last_message_end(rom, o, limit=0x3000):
    """End of a block's last message: after the first 」FFFF not followed by FF18."""
    for p in range(o, o + limit, 2):
        if word(rom, p) == RBRACKET and word(rom, p + 2) == FFFF and word(rom, p + 4) != FF18:
            return p + 4
    raise ValueError(f"no message end within {limit:#x} bytes of {o:#x}")


def read_slots(rom):
    return [rom[p] | rom[p + 1] << 8 | rom[p + 2] << 16 for p in range(MASTER_TABLE, MASTER_END, 3)]


def unpack_master(rom, codec):
    slots = read_slots(rom)
    offs = sorted({to_file(v) for v in slots if v})
    groups, cur = [], [offs[0]]
    for o in offs[1:]:
        if o - cur[-1] < BLOCK_GAP:
            cur.append(o)
        else:
            groups.append(cur)
            cur = [o]
    groups.append(cur)
    starts = tuple(g[0] for g in groups)
    if starts != MASTER_BLOCKS:
        raise ValueError("master blocks moved: " + " ".join("%06X" % s for s in starts))
    blocks, where = [], {}
    for bi, g in enumerate(groups):
        ends = g[1:] + [last_message_end(rom, g[-1])]
        msgs = []
        for mi, (s, e) in enumerate(zip(g, ends)):
            where[s] = (bi, mi)
            msgs.append(codec.decode(words_at(rom, s, e)))
        blocks.append({"start": g[0], "end": ends[-1], "msgs": msgs})
    # slot -> [block, message] or None; several slots may share one message.
    slot_map = [list(where[to_file(v)]) if v else None for v in slots]
    return {"blocks": blocks, "slots": slot_map}


def unpack(rom, codec=None):
    codec = codec or WordCodec()
    regions = [{"name": n, "start": s, "end": e, "text": codec.decode(words_at(rom, s, e))} for n, s, e in REGIONS]
    return {"master": unpack_master(rom, codec), "regions": regions}


def repack(rom, data, codec=None):
    codec = codec or WordCodec()
    out = bytearray(rom)
    for r in data["regions"]:
        b = codec.encode_bytes(r["text"])
        if len(b) != r["end"] - r["start"]:
            raise ValueError(f"region {r['name']}: {len(b)} bytes, slot is {r['end'] - r['start']}")
        out[r["start"]:r["end"]] = b
    m = data["master"]
    addr = {}
    spill = EXPANDED_TEXT[0]
    for bi, blk in enumerate(m["blocks"]):
        p = blk["start"]
        for mi, text in enumerate(blk["msgs"]):
            b = codec.encode_bytes(text)
            if p + len(b) <= blk["end"]:          # in place while the block has room
                addr[(bi, mi)] = p
                out[p:p + len(b)] = b
                p += len(b)
                continue
            p = blk["end"]                       # the rest of this block's messages go to the expanded ROM
            if len(out) < ROM_EXPANDED:          # 3 MB -> 4 MB: banks $F0-$FF, filled with FF
                out += b"\xff" * (ROM_EXPANDED - len(out))
            if (spill >> 16) != ((spill + len(b) - 1) >> 16):
                spill = (spill + 0xFFFF) & ~0xFFFF    # a message never crosses a bank
            if spill + len(b) > EXPANDED_TEXT[1]:
                raise ValueError(f"expanded text area full at master message {bi}/{mi}")
            addr[(bi, mi)] = spill
            out[spill:spill + len(b)] = b
            spill += len(b)
        # Unused tail after a shrunk block: original bytes stay (nothing points there).
    for i, ref in enumerate(m["slots"]):
        v = to_cpu(addr[tuple(ref)]) if ref is not None else 0
        out[MASTER_TABLE + 3 * i:MASTER_TABLE + 3 * i + 3] = v.to_bytes(3, "little")
    return bytes(out)
