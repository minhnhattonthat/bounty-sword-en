"""script_text.py: the text layer between the ROM layout (tools/rom_text.py) and the script/ files.

    from script_text import extract, apply_script
    files = extract(rom)              # {"master_1E0000.json": [entry, ...], "locations.json": [...], ...}
    data = apply_script(rom, files)   # rom_text.unpack() layout with every entry's jp re-encoded

Every entry's `jp` is a lossless rendering of its words: encode(decode(words)) == words for every string in the ROM
(tests/test_script.py), and the entries tile every text range with no gap (the coverage test).

Text tokens (docs/re/text.md):
- master dialogue (engine A): newline = FFFF (line end / page wait), `　` = 0000 (space), `‥` = 0400,
  `{spk}` = FF15 (speaker header: a name word or 6 literal name words, then a newline), `{next}` = FF18 (next box),
  `{end}` = FF00, `{hero}` = the run FF19..FF1E (hero name), `{FFxx}` = any other control word, `{FFxx:hhhh}` = a
  control word with its argument words, `[hhhh]` = any word with no character (unidentified kanji, data).
- side tables: the same except FFFF stays `{FFFF}` and no argument parsing; fixed-width entries drop their trailing
  0000 padding (re-padded on encode) and keep extra data words in `tail`.
A table character that collides with an alias (`　` 0001, `‥` 0045) is written as `[hhhh]`, so tokens never clash.
"""
import json
from pathlib import Path

from font_en import EN_BASE, FIRST as EN_FIRST, LAST as EN_LAST
from rom_text import REGIONS, TBL, WordCodec, unpack, word, words_at

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"

# Engine A argument words per opcode (docs/re/text.md §Engine A). Opcodes with conditional or byte-sized arguments
# never occur in the master text; decoding refuses them so a new table can't silently desync.
ENGINE_A_ARGS = {0xFF05: 1, 0xFF06: 1, 0xFF09: 1, 0xFF0A: 1, 0xFF0B: 1, 0xFF0C: 1, 0xFF14: 1}
ENGINE_A_UNPARSED = {0xFF0F, 0xFF10, 0xFF25, 0xFF26, 0xFF27, 0xFF29, 0xFF2A, 0xFF2D}
HERO_RUN = (0xFF19, 0xFF1A, 0xFF1B, 0xFF1C, 0xFF1D, 0xFF1E)
NAMED = {0xFF15: "spk", 0xFF18: "next", 0xFF00: "end"}
NAME_WORDS = set(range(0xFF1F, 0xFF25)) | {0xFF28, 0xFF31}
SPACE, LEADER = 0x0000, 0x0400
# Engine B (interpreter C3:C6BF, word reader C3:C78B) argument words per opcode (docs/re/text.md §Engine B).
ENGINE_B_ARGS = {0xFF04: 1, 0xFF06: 2, 0xFF08: 1, 0xFF09: 5, 0xFF0B: 4, 0xFF0C: 2, 0xFF0E: 1, 0xFF10: 2}


class TextCodec:
    """Word list <-> readable text, lossless. `master=True` adds the engine A tokens; `args` parses the argument
    words of a side table's script engine (ENGINE_B_ARGS) into `{FFxx:hhhh...}`."""

    def __init__(self, master, path=TBL, args=None):
        base = WordCodec(path)
        self.master = master
        self.args = args or {}
        self.dec = dict(base.dec)
        self.char = {SPACE: "　", LEADER: "‥"}
        if master:
            self.char[0xFFFF] = "\n"
        taken = set(self.char.values())
        self.dec = {w: c for w, c in self.dec.items() if c not in taken}
        self.dec.update(self.char)
        self.enc = {c: w for w, c in self.dec.items()}
        # English (tools/font_en.py): ASCII c -> EN_BASE + ord(c). Encode only: JP decoding never yields ASCII,
        # and words in that range inside JP data stay `[hhhh]`.
        for code in range(EN_FIRST, EN_LAST + 1):
            if chr(code) not in "{}[]":
                self.enc[chr(code)] = EN_BASE + code
        self.named = {v: k for k, v in NAMED.items()} if master else {}

    def decode(self, words):
        out, i, n = [], 0, len(words)
        while i < n:
            w = words[i]
            if self.master and w == HERO_RUN[0] and tuple(words[i:i + 6]) == HERO_RUN:
                out.append("{hero}")
                i += 6
                continue
            if w >= 0xFF00 and w != 0xFFFF or (w == 0xFFFF and not self.master):
                if self.master and w in ENGINE_A_UNPARSED:
                    raise ValueError(f"engine A opcode {w:04X} has unparsed arguments")
                k = ENGINE_A_ARGS.get(w, 0) if self.master else self.args.get(w, 0)
                args = words[i + 1:i + 1 + k]
                if len(args) < k and self.master:
                    raise ValueError(f"opcode {w:04X} cut short")
                name = NAMED.get(w) if self.master and not k else None
                out.append("{%s}" % name if name else "{%04X%s}" % (w, "".join(":%04X" % a for a in args)))
                i += 1 + k
                continue
            out.append(self.dec[w] if w in self.dec else "[%04X]" % w)
            i += 1
        return "".join(out)

    def encode(self, text):
        out, i = [], 0
        while i < len(text):
            c = text[i]
            if c == "{":
                j = text.index("}", i)
                tag = text[i + 1:j]
                if tag == "hero" and self.master:
                    out += HERO_RUN
                elif tag in self.named:
                    out.append(self.named[tag])
                else:
                    parts = [int(p, 16) for p in tag.split(":")]
                    if parts[0] < 0xFF00:
                        raise ValueError(f"{{{tag}}}: braces hold FFxx control words")
                    out += parts
                i = j + 1
            elif c == "[":
                j = text.index("]", i)
                out.append(int(text[i + 1:j], 16))
                i = j + 1
            elif c in self.enc:
                out.append(self.enc[c])
                i += 1
            else:
                raise ValueError(f"unencodable {c!r} at {i} in {text!r}")
        return out


# Side tables: how each region of rom_text.REGIONS splits into entries.
#   ("fixed", width, tail[, lead]): width-word records from `lead` words in; the last `tail` words are data.
#   ("term",): a string ends after a run of 0000 words.
#   ("ends", {words}): a string ends after any of these control words.
#   ("counted",): [count][count words] strings back to back; anything that breaks the chain is a 1-word entry.
#   ("data",): one data entry (no text).
#   ("anchored",): [count][count words] strings only where a C8 window script's op 02 points (`window_anchors`);
#       every stretch between them is one data entry (tile/layout tables: tools/re/winscript.py, docs/re/vwf.md).
SPLIT = {
    "locations": ("fixed", 10, 0),
    "battle_prompts_b": ("ends", {0xFF00, 0xFF03}),
    "menus": ("anchored",),
    "windows": ("anchored",),
    "menus_c": ("anchored",),
    "speakers": ("fixed", 8, 2, 8),     # records (6-word name + 2 ids) start at 0x025D6D = C2:5D6D

    "system_prompts": ("ends", {0xFF00, 0xFF03}),
    "unit_records": ("term",),
    "battle_prompts": ("ends", {0xFF00, 0xFF03}),
    "unit_names": ("fixed", 6, 0),
    "unit_titles": ("fixed", 16, 0, 10),
    "spells": ("fixed", 10, 0),
    "c8_layout": ("data",),
    "constellations": ("fixed", 5, 0),
    "c8_digits": ("data",),
    "orders": ("fixed", 8, 0),
    "classes": ("fixed", 10, 0),
    "descriptions": ("ends", {0xFF00, 0xFF0D, 0xFF03}),
    "objectives": ("ends", {0xFFFE, 0xFFFF}, "ptr16"),
    "items": ("fixed", 10, 0),
    "short_strings": ("ends", {0xFF0D, 0xFF07, 0xFF03}),
    "ceremony": ("ends", {0xFF0D, 0xFF07, 0xFF03}),
}
# Tables run by engine B: verified for ceremony and short_strings (read by C3:C78B in the region-read tour,
# tools/re/region_reads.py); descriptions per docs/re/text.md (FF06 calls), not yet seen read.
ENGINE_B_TABLES = {"ceremony", "short_strings", "descriptions"}


def split_region(words, rule, args=None, anchors=()):
    """Word index ranges [(a, b), ...] that tile the region. `args`: argument counts to step over when looking
    for end words. `anchors`: word indices where an "anchored" region's counted strings start."""
    n, cuts = len(words), [0]
    kind = rule[0]
    if kind == "data":
        return [(0, n)]
    if kind == "anchored":
        for a in sorted(anchors):
            c = words[a]
            if a + 1 + c > n:
                raise ValueError(f"anchored string at word {a} runs past the region ({c} words)")
            cuts += [a, a + 1 + c]
        cuts = sorted(set(c for c in cuts if c < n))
        return list(zip(cuts, cuts[1:] + [n]))
    if kind == "ends" and args:
        i = 0
        while i < n:
            w = words[i]
            i += 1 + args.get(w, 0)
            if w in rule[1] and i < n:
                cuts.append(i)
        cuts = sorted(set(cuts))
        return list(zip(cuts, cuts[1:] + [n]))
    if kind == "counted":
        i = 0
        while i < n:
            cuts.append(i)
            c = words[i]
            i += 1 + c if 0 < c < 0x100 and i + 1 + c <= n else 1
    elif kind == "fixed":
        width, lead = rule[1], (rule[3] if len(rule) > 3 else 0)
        cuts += [lead] if lead else []
        cuts += list(range(lead + width, n, width))
    elif kind == "term":
        for i in range(1, n):
            if words[i - 1] == 0 and words[i] != 0:
                cuts.append(i)
    else:
        cuts += [i + 1 for i in range(n - 1) if words[i] in rule[1]]
        if "ptr16" in rule:  # a run of 16-bit pointers ($FD00-$FFFD lo words) inside the table is its own entry
            ptr = [0xFD00 <= w < 0xFFFE for w in words]
            cuts += [i for i in range(1, n) if ptr[i] != ptr[i - 1] and (ptr[i] or words[i - 1] not in rule[1])]
    cuts = sorted(set(c for c in cuts if 0 <= c < n))
    return list(zip(cuts, cuts[1:] + [n]))


def is_data(words, args=None):
    """Words no glyph can be (0x0500-0xFEFF, outside control arguments), or nothing but fill: not text."""
    if all(w in (0, 0xFFFF) for w in words):
        return True
    args, i = args or {}, 0
    while i < len(words):
        w = words[i]
        if 0x0500 <= w < 0xFF00 and w != LEADER:
            return True
        i += 1 + args.get(w, 0)
    return False


def side_codecs():
    """(plain side-table codec, engine B codec), indexed by `name in ENGINE_B_TABLES`."""
    return TextCodec(False), TextCodec(False, args=ENGINE_B_ARGS)


def pointer_index(rom):
    """24-bit little-endian value -> file offsets holding it, for the HiROM $C0-$FF and $40-$7D mirrors."""
    idx = {}
    for p in range(len(rom) - 2):
        b = rom[p + 2]
        if 0xC0 <= b or 0x40 <= b < 0x7E:
            idx.setdefault(rom[p] | rom[p + 1] << 8 | (b & 0x3F) << 16, []).append(p)
    return idx


WINDOW_SCRIPTS = (0x080000, 0x090000)    # C8: the C1 window scripts (interpreter C1:870C)


def window_anchors(rom, start, end):
    """Word indices in [start, end) that a window-script op 02 (`02 pos16 ptr24`, drawer C1:8F13) points at, with a
    count word 1-255. Op 02 is the only window op pointing into the C1 string area, and no code loads a pointer
    there (2026-11-22 sweep), so these are all the strings the C1 regions hold."""
    out = set()
    lo, hi = WINDOW_SCRIPTS
    for p in range(lo, hi - 5):
        if rom[p] == 0x02 and rom[p + 5] in (0xC1, 0x41):
            t = 0x010000 | rom[p + 4] << 8 | rom[p + 3]
            if start <= t < end and (t - start) % 2 == 0 and 0 < word(rom, t) < 0x100:
                out.add((t - start) // 2)
    return out


def side_entries(rom, name, start, end, codec, ptrs):
    words = words_at(rom, start, end)
    rule = SPLIT[name]
    args = ENGINE_B_ARGS if name in ENGINE_B_TABLES else None
    codec = codec[bool(args)]
    anchors = window_anchors(rom, start, end) if rule[0] == "anchored" else set()
    out = []
    for a, b in split_region(words, rule, args, anchors):
        w = words[a:b]
        off = start + 2 * a
        e = {"id": "%06X" % off}
        tail = []
        if rule[0] == "fixed" and b - a == rule[1]:
            e["width"] = rule[1] - rule[2]
            body = w[:e["width"]]
            tail = w[e["width"]:]
            while body and body[-1] == 0:
                body = body[:-1]
            w = body
        counted = (rule[0] == "counted" and b - a > 1) or a in anchors
        if counted:           # count word kept as `head`; the body is fixed at that many words, 0000 = space
            e["head"] = "%04X" % w[0]
            e["width"] = b - a - 1
            w = w[1:]
            while w and w[-1] == 0:
                w = w[:-1]
        if rule[0] == "data":
            e["kind"] = "data"
        elif rule[0] in ("counted", "anchored"):
            e["kind"] = "text" if counted and off in ptrs and not is_data(w, args) else "data"
        else:
            e["kind"] = "data" if is_data(words[a:b], args) else "text"
        e["jp"] = codec.decode(w)
        if tail:
            e["tail"] = " ".join("%04X" % t for t in tail)
        if e["kind"] == "text":
            e["en"] = ""
        refs = ptrs.get(off, [])
        if refs:
            e["refs"] = ["%06X" % r for r in refs]
        out.append(e)
    return out


# Tables drawn by the C1 string runs (asm/vwf.asm C1Run): English there is proportional inside the field's cells,
# two ASCII letters may share a word, and `[0F7F]` (TAB) moves to the next cell (grid strings cut into slices).
C1_TABLES = {"items", "classes", "unit_names", "unit_titles", "spells", "constellations", "orders", "windows", "menus",
             "menus_c"}
TAB = 0x0F7F


def pack_pairs(words):
    """Two English letters in a row -> one word (first << 8 | second), each letter as ASCII."""
    out, i = [], 0
    while i < len(words):
        a = words[i]
        b = words[i + 1] if i + 1 < len(words) else None
        if b is not None and EN_BASE + EN_FIRST <= a <= EN_BASE + EN_LAST and EN_BASE + EN_FIRST <= b <= EN_BASE + EN_LAST:
            out.append((a - EN_BASE) << 8 | (b - EN_BASE))
            i += 2
        else:
            out.append(a)
            i += 1
    return out


def side_words(entry, codec, pack=False):
    w = codec.encode(entry["jp"])
    if pack and "width" in entry:     # only fixed fields: a run with no width keeps its JP length
        w = pack_pairs(w)
    if "width" in entry:
        if len(w) > entry["width"]:
            raise ValueError(f"{entry['id']}: {len(w)} words, field is {entry['width']}")
        w = w + [0] * (entry["width"] - len(w))
    if entry.get("tail"):
        w = w + [int(t, 16) for t in entry["tail"].split()]
    if entry.get("head"):
        w = [int(entry["head"], 16)] + w
    return w


def extract(rom):
    """Every text entry, grouped by script file name."""
    mc, sc = TextCodec(True), side_codecs()
    data = unpack(rom)
    files = {}
    m = data["master"]
    by_msg = {}
    for i, ref in enumerate(m["slots"]):
        if ref is not None:
            by_msg.setdefault(tuple(ref), []).append(i)
    for bi, blk in enumerate(m["blocks"]):
        entries, p = [], blk["start"]
        for mi, raw in enumerate(blk["msgs"]):
            w = WordCodec().encode(raw)
            entries.append({"id": "%06X" % p, "slots": by_msg[(bi, mi)], "jp": mc.decode(w), "en": ""})
            p += 2 * len(w)
        files["master_%06X.json" % blk["start"]] = entries
    ptrs = pointer_index(rom)
    for name, s, e in REGIONS:          # a name listed twice (word-phase segments) fills one file
        files.setdefault(name + ".json", []).extend(side_entries(rom, name, s, e, sc, ptrs))
    return files


def write_file(path, entries):
    path.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def dump(rom, out=SCRIPT, force=False, refresh=False):
    """Write script/*.json. Never overwrites a file (English may be in it) unless force. `refresh` re-renders every
    entry's jp (after a table change) and keeps en/notes; returns (files written, ids whose jp changed under an en)."""
    out.mkdir(parents=True, exist_ok=True)
    written, requeue = [], []
    for name, entries in extract(rom).items():
        path = out / name
        if path.exists() and not force:
            if not refresh:
                continue
            old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
            if set(old) != {e["id"] for e in entries}:
                raise ValueError(f"{name}: entry ids changed; refresh can't carry English across a re-split")
            for e in entries:
                o = old[e["id"]]
                if o.get("en") and o["jp"] != e["jp"]:
                    requeue.append(e["id"])
                e.update({k: v for k, v in o.items() if k not in e or k in ("en", "notes", "status")})
        write_file(path, entries)
        written.append(name)
    return written, requeue


def load(src=SCRIPT):
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(src).glob("*.json"))}


def region_entries(files, name, start, end):
    """The entries of script file `name` that lie in the region segment [start, end)."""
    return [e for e in files[name + ".json"] if start <= int(e["id"], 16) < end]


OVERFLOW = []   # side entries whose `en` overflowed a fixed field in the last apply_script (JP kept)


def apply_script(rom, files, field="jp"):
    """rom_text.unpack() layout with each entry's `field` encoded back in (the build's text step)."""
    OVERFLOW.clear()
    mc, sc, wc = TextCodec(True), side_codecs(), WordCodec()
    data = unpack(rom)
    for bi, blk in enumerate(data["master"]["blocks"]):
        entries = files["master_%06X.json" % blk["start"]]
        if len(entries) != len(blk["msgs"]):
            raise ValueError(f"master block {blk['start']:06X}: {len(entries)} entries, layout has {len(blk['msgs'])}")
        blk["msgs"] = [wc.decode(mc.encode(e[field] if e.get(field) else e["jp"])) for e in entries]
    for r in data["regions"]:
        words = []
        for e in region_entries(files, r["name"], r["start"], r["end"]):
            src = dict(e, jp=e[field]) if e.get(field) else e
            codec, pack = sc[r["name"] in ENGINE_B_TABLES], r["name"] in C1_TABLES
            try:
                words += side_words(src, codec, pack=pack)
            except ValueError:
                if src is e:
                    raise
                # English longer than a fixed field the engine can't widen yet (speaker tags, location labels:
                # decision D8, phase 7): keep the JP and report it.
                OVERFLOW.append(f"{r['name']}:{e['id']}")
                words += side_words(e, codec, pack=pack)
        r["text"] = wc.decode(words)
    return data
