"""marker.py: the marker build's text (build.py --marker). Every text entry's `en` becomes a marker that shows its id.

    from marker import marker_files
    files = marker_files(load(SCRIPT))       # copies; script/ is never written

- Master dialogue (engine A, VWF): each box keeps its structure (speaker header verbatim, control words, the same
  number of lines, a closing 」 where the line had one, since C2:48B3 tests it) and each line is filled to exactly
  LINE_PX pixels; the box's first line starts with `<id>.<box>`, every line ends in `|` so a clipped end shows.
- Side tables: fixed-width records get `<tag><index>` padded with letters to the full field width; variable-length
  strings (repacked in place) keep their exact word count: each character becomes the next letter of
  `<tag><index>abc...`, control words and 0000 words stay.
"""
import copy
import re

from font_en import advance

LINE_PX = 160          # 20 cells; the width gate (docs/re/vwf.md) checks it in game
TAGS = {"locations": "L", "battle_prompts_b": "P", "menus": "M", "speakers": "K", "system_prompts": "Z",
        "unit_records": "R", "battle_prompts": "B", "unit_names": "N", "unit_titles": "T", "classes": "C",
        "descriptions": "D", "objectives": "O", "items": "I", "short_strings": "S", "ceremony": "Y"}
FILL = "The quick brown fox jumps over the lazy dog. "
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]|\n|.", re.S)
NAME_TOKENS = {"{hero}"} | {"{FF%02X}" % c for c in (0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x28, 0x31)}
CLOSE = "」"           # draws as '"' in the VWF (asm/vwf.asm)
KEEP_JP = {"speakers"}  # FF15 literal names in the master text must match this table (portraits)


def fill_line(head, px, tail=""):
    """head + filler + tail, exactly px pixels wide (within the font's 1-px granularity)."""
    adv = advance()
    out, used = head, sum(adv[c] for c in head) + sum(adv.get(c, adv['"']) for c in tail)
    i = 0
    while True:
        c = FILL[i % len(FILL)]
        if used + adv[c] > px - adv["|"]:
            break
        out += c
        used += adv[c]
        i += 1
    out = out.rstrip()
    room = px - adv["|"] - sum(adv[c] for c in out) - sum(adv.get(c, adv['"']) for c in tail)
    while room >= 2:                 # top up with 2-px dots, a 3-px comma for an odd remainder
        if room == 3 or room % 2:
            out += ","
            room -= adv[","]
        else:
            out += "."
            room -= adv["."]
    return out + "|" + tail


def wrap_px(text, px):
    """Greedy wrap by characters (not words) into lines of at most px pixels."""
    adv, lines, cur = advance(), [], ""
    for c in text:
        if sum(adv[x] for x in cur + c) > px:
            lines.append(cur)
            cur = ""
        cur += c
    return lines + [cur]


# Glyph torture box (pipeline.md §Width gate): every printable ASCII the script can encode ({}[] are script syntax)
# and double spaces, shown first in the prologue (scene `prologue`, message 24FABE, box 1).
TORTURE_ID = "24FABE"
TORTURE = "".join(chr(c) for c in range(0x20, 0x7F) if chr(c) not in "{}[]") + "  two  spaces  end"


def torture_boxes():
    """The torture text as boxes of at most 3 lines, each box closed by 」 like the game's own."""
    lines = wrap_px(TORTURE, LINE_PX - 8)
    boxes = ["\n".join(lines[i:i + 3]) + CLOSE + "\n" for i in range(0, len(lines), 3)]
    return "{next}\n".join(boxes)


# Chapter-card subtitles (mode 14, printer C6:DD44, glyphs C6:DF04 -> the VWF): line 1 centred by its pixel width
# (C6:D383 hook), later lines start at the left edge. Messages = master pointer slots listed by the card table
# C6:D485 (60 words, byte offsets into the master pointer table). docs/re/vwf.md §Width gate.
CARD_TABLE, CARD_COUNT = 0x06D485, 60
QUOTE_PX = {"「": None, "」": None, "[0405]": 8, "[0406]": 8}   # None: drawn as '"'


def card_slots(rom):
    return {int.from_bytes(rom[CARD_TABLE + 2 * i:CARD_TABLE + 2 * i + 2], "little") // 3
            for i in range(1, CARD_COUNT)}


def card_marker(eid, jp):
    """Each line filled to LINE_PX, quotes kept; line 1 starts with the id."""
    adv = advance()
    out = []
    for n, line in enumerate(jp.rstrip("\n").split("\n")):
        toks = TOKEN.findall(line)
        head = toks[0] if toks[0] in QUOTE_PX else ""
        tail = toks[-1] if toks[-1] in QUOTE_PX else ""
        px = LINE_PX - sum(QUOTE_PX[q] or adv['"'] for q in (head, tail) if q)
        out.append(head + fill_line(f"{eid} " if n == 0 else "", px) + tail)
    return "\n".join(out) + "\n"


def master_marker(eid, jp, torture=True):
    if eid == TORTURE_ID and torture:
        head, _, rest = jp.partition("\n")       # keep the speaker header, replace box 1, mark the rest
        return head + "\n" + torture_boxes() + "{next}" + master_marker(eid, rest.split("{next}", 1)[1], False)
    toks = TOKEN.findall(jp)
    out, line, box, li, header = [], [], 1, 0, False

    def flush():
        nonlocal li
        ctrl = [t for t in line if t.startswith("{") and t not in NAME_TOKENS]
        chars = [t for t in line if not t.startswith("{")]
        if chars:
            tail = CLOSE if chars[-1] == CLOSE else ""
            head = f"{eid}.{box} " if li == 0 else ""
            out.append("".join(ctrl) + fill_line(head, LINE_PX, tail))
            li += 1                  # the FFFF right after FF18 is no text line
        else:
            out.append("".join(ctrl))
        line.clear()

    for t in toks:
        if header:
            out.append(t)
            if t == "\n":
                header = False
            continue
        if t == "{spk}":
            out.append(t)
            header = True
        elif t == "{next}":
            if line:
                flush()
            out.append(t)
            box, li = box + 1, 0
        elif t == "\n":
            flush()
            out.append("\n")
        else:
            line.append(t)
    if line:
        flush()
    return "".join(out)


def side_marker(tag, idx, entry):
    label = f"{tag}{idx}"
    letters = label + "abcdefghijklmnopqrstuvwxyz" * 4
    toks = TOKEN.findall(entry["jp"])
    if "width" in entry:
        return (label + "abcdefghijklmnopqrstuvwxyz")[:entry["width"]]
    out, k = [], 0
    for t in toks:
        if t.startswith("{") or t in ("　", "\n"):
            out.append(t)
        else:
            out.append(letters[k % len(letters)])
            k += 1
    return "".join(out)


def marker_files(files, rom):
    """rom = the original dump (card_slots reads the chapter-card table from it)."""
    files = copy.deepcopy(files)
    cards = card_slots(rom)
    for name, entries in files.items():
        if name.startswith("master_"):
            for e in entries:
                card = cards & set(e.get("slots", []))
                e["en"] = card_marker(e["id"], e["jp"]) if card else master_marker(e["id"], e["jp"])
            continue
        if name[:-5] in KEEP_JP:
            continue
        tag = TAGS[name[:-5]]
        for i, e in enumerate(entries):
            if e.get("kind") == "text" and e["jp"]:
                e["en"] = side_marker(tag, i, e)
    return files
