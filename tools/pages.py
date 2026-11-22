"""pages.py: master dialogue as pages (author boxes, generate lines).

A master message (script/master_*.json `jp`, tokens in tools/script_text.py) is lines split by FFFF ("\n"):
speaker headers (`{spk}...`), control-only lines (`{next}`, `{end}`, ...) and text lines. A run of text lines is one
*page* (one dialogue box in the JP). Translators write the English of each page as one paragraph; `build_en` wraps it
to the box (LINE_PX a line, LINES lines a box), splits a page that needs more boxes with `」\n{next}\n「` like the
game's own boxes, and puts it back into the message skeleton, so headers and control codes never pass through a
translator's hands.

    from pages import split, jp_view, build_en
    jp_view(jp)                      # "<ミランダ> 「ここは…」 ‖ 「…」" (batch view)
    en, problems = build_en(jp, '"This is the capital." || "There is a tavern here."')

English page syntax: plain ASCII; a page starting/ending with `"` where the JP page has 「/」 gets them back as the
structural 「」 (drawn as '"', C2:48B3 ends a speech on 」 FFFF). Name words ({hero} {FF31} {FF1F}..) stay inline.
`\\n` forces a line break; `{next}` inside a page forces a new box. A page whose first line starts with {FF2F}/{FF30}
(conditional lines: skip to after the next FF18 FFFF) keeps that prefix and must fit one line, never split.
Messages with mid-line control codes (yes/no prompts) are `raw`: their English is the whole message in script syntax.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font_en import advance  # noqa: E402

TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]|\n|.", re.S)
LINE_PX = 158          # box is 160 px (docs/re/vwf.md width gate); keep 2 px off the edge
LINES = 3              # lines a box
# Inline name/number words and their worst-case pixel widths (hero name: 6 letters; numbers: 3 digits).
INLINE_PX = {"{hero}": 42, "{FF31}": 48, "{FF1F}": 48, "{FF20}": 48, "{FF21}": 48, "{FF22}": 48, "{FF23}": 48,
             "{FF24}": 48, "{FF28}": 48, "{FF2B}": 18, "{FF2C}": 18}
PREFIX = {"{FF2F}", "{FF30}", "{FF12}"}   # control words that may lead a text line
NOSPLIT = {"{FF2F}", "{FF30}"}
SEP = " || "
_ADV = None


def adv():
    global _ADV
    if _ADV is None:
        _ADV = advance()
    return _ADV


def px(text):
    """Pixel width of one line of English (script syntax)."""
    a, w = adv(), 0
    for t in TOKEN.findall(text):
        if t in INLINE_PX:
            w += INLINE_PX[t]
        elif t in "「」":
            w += a['"']
        elif t == "　":
            w += 8
        elif t.startswith("{") or t.startswith("[") and len(t) > 1:
            w += 0 if t.startswith("{") else 8
        else:
            w += a.get(t, 8)
    return w


def is_ctrl(t):
    return t.startswith("{") and t not in INLINE_PX


def split(jp):
    """(raw, items): items are ("line", text) for kept lines and ("page", prefix, [lines]) for text pages."""
    items, raw = [], False
    for line in jp.split("\n"):
        toks = TOKEN.findall(line)
        if line.startswith("{spk}") or not toks or all(is_ctrl(t) for t in toks):
            items.append(("line", line))
            continue
        k = 0
        while k < len(toks) and toks[k] in PREFIX:
            k += 1
        prefix, body = "".join(toks[:k]), toks[k:]
        if any(is_ctrl(t) for t in body):
            raw = True
        if prefix or not items or items[-1][0] != "page":
            items.append(("page", prefix, ["".join(body)]))
        else:
            items[-1][2].append("".join(body))
    return raw, items


def speaker(header, names=None):
    name = header[len("{spk}"):].rstrip("　 ")
    return (names or {}).get(name, name)


def jp_view(jp, names=None):
    """One-line batch view: pages joined by ' ‖ ', speaker headers as <name>, line breaks as ' / '."""
    raw, items = split(jp)
    if raw:
        return "RAW " + jp.replace("\n", "\\n")
    out, spk = [], ""
    for it in items:
        if it[0] == "line":
            if it[1].startswith("{spk}"):
                spk = f"<{speaker(it[1], names)}> "
            continue
        lines = [ln.lstrip("　") for ln in it[2]]
        out.append(spk + it[1] + " / ".join(lines))
        spk = ""
    return " ‖ ".join(out)


def wrap(text, lead="", indent="", reserve=0):
    """Greedy word wrap of one paragraph to LINE_PX - reserve; line 1 starts after `lead`, later lines with `indent`
    (both counted, neither returned in line 1). `\\n` forces a break."""
    lines = []
    for para in text.split("\\n"):
        cur = None
        for word in para.split(" "):
            if cur is None:
                cur = word if not lines else indent + word
                continue
            head = lead if not lines else ""
            if px(head + cur + " " + word) + reserve <= LINE_PX:
                cur += " " + word
            else:
                lines.append(cur)
                cur = indent + word
        lines.append(cur or "")
    return lines


def layout_page(jp_lines, prefix, en, menu=False):
    """English page -> (list of output lines incl. {next} splits, problems)."""
    probs = []
    jp_text = "".join(jp_lines)
    q_open, q_close = jp_text.startswith("「"), jp_text.endswith("」")
    en = en.strip()
    if q_open:
        if not en.startswith('"'):
            probs.append("page must open with a quote like the JP 「")
        en = en[1:] if en.startswith('"') else en
    if q_close:
        if not en.endswith('"'):
            probs.append("page must close with a quote like the JP 」")
        en = en[:-1] if en.endswith('"') else en
    boxes_src = [b.strip() for b in en.split("{next}")]
    boxes = []
    for b in boxes_src:
        lines = wrap(b, "「" if q_open else "", " " if q_open else "", px("」") if q_close else 0)
        chunks = [lines[i:i + LINES] for i in range(0, len(lines), LINES)]
        for c in chunks[1:]:          # a box that starts mid-paragraph gets its own 「, no indent
            c[0] = c[0].lstrip(" ")
        boxes += chunks
    if (prefix and any(p in prefix for p in NOSPLIT)) and (len(boxes) > 1 or len(boxes[0]) > 1):
        probs.append("conditional line ({FF2F}/{FF30}) must fit one line")
    # A choice list (page right before a {FF14} choice code, JP lines indented for the cursor): keep that indent on
    # every English line, one option a line.
    if menu and all(ln.startswith("　") for ln in jp_lines):
        boxes = [["　" + ln.lstrip(" ") for ln in box] for box in boxes]
    out = []
    for i, box in enumerate(boxes):
        box = list(box)
        if q_open and (i == 0 or q_close):
            box[0] = "「" + box[0]
        if q_close and (i == len(boxes) - 1 or q_open):
            box[-1] = box[-1] + "」"
        for ln in box:
            if px(ln) > LINE_PX + (px("」") if ln.endswith("」") else 0):
                probs.append(f"line over {LINE_PX} px ({px(ln)}): {ln!r}")
        if i:
            out.append("{next}")
        out += box
    out[0] = prefix + out[0]
    return out, probs


WIDOW_CHARS = 20   # a continuation box of one line this short that starts mid-sentence is a widow
SENTENCE_END = re.compile(r"(?:[.!?]|\.\.\.)['\"]?$")


def widows(jp, en):
    """Continuation boxes the wrap adds (not a forced {next}) that hold one short line starting mid-sentence:
    "...the twelve" / "powers of darkness!". Each costs the player a key press for a word or two (review of phase 6).
    Returns ["page N: 'text'"]; raw messages and choice/conditional pages are skipped."""
    raw, items = split(jp)
    if raw:
        return []
    pages = [p for p in items if p[0] == "page"]
    src = [p.strip() for p in en.split("||")]
    if len(src) != len(pages):
        return []
    out = []
    for k, (it, text) in enumerate(zip(pages, src)):
        jp_text = "".join(it[2])
        q_open, q_close = jp_text.startswith("「"), jp_text.endswith("」")
        body = text.strip()
        body = body[1:] if q_open and body.startswith('"') else body
        body = body[:-1] if q_close and body.endswith('"') else body
        for b in body.split("{next}"):
            lines = wrap(b.strip(), "「" if q_open else "", " " if q_open else "", px("」") if q_close else 0)
            chunks = [lines[i:i + LINES] for i in range(0, len(lines), LINES)]
            for prev, c in zip(chunks, chunks[1:]):
                short = len(re.sub(r"\{[^}]*\}", "xxxxxx", c[0].strip())) <= WIDOW_CHARS
                if len(c) == 1 and short and not SENTENCE_END.search(prev[-1].strip()):
                    out.append(f"page {k + 1}: {c[0].strip()!r}")
    return out


def build_en(jp, en):
    """Full English message from the page paragraphs ('||'-separated) or, for raw messages, script syntax."""
    raw, items = split(jp)
    if raw:
        return en.replace("\\n", "\n"), []
    pages = [p for p in items if p[0] == "page"]
    src = [p.strip() for p in en.split("||")]
    if len(src) != len(pages):
        return None, [f"{len(src)} English pages for {len(pages)} JP pages"]
    out, probs, k = [], [], 0
    for n, it in enumerate(items):
        if it[0] == "line":
            out.append(it[1])
            continue
        after = items[n + 1] if n + 1 < len(items) else None
        menu = bool(after) and after[0] == "line" and after[1].startswith("{FF14")
        lines, p = layout_page(it[2], it[1], src[k], menu)
        probs += [f"page {k + 1}: {x}" for x in p]
        out += lines
        k += 1
    return "\n".join(out), probs
