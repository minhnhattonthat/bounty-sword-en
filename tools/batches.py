"""batches.py: translation batches for script/*.json (adapted from the skill's assets/batches.py).

    python -X utf8 tools/batches.py split [--size 3500] [--only master|side|FILE]   -> work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check b001 [b002 ...]   # until it prints OK
    python -X utf8 tools/batches.py merge b001 [--overwrite]
    python -X utf8 tools/batches.py check                   # every English entry in script/
    python -X utf8 tools/batches.py rewrap                  # after a pages.py change: re-lay out merged pages
    python -X utf8 tools/batches.py --selftest

Batch TSV: id, speaker, form, limit, JP. Output work/tl/bNNN.out.tsv: id<TAB>English, every id once, same order.
Master dialogue (form `dlg`): JP is the page view of tools/pages.py (pages ' ‖ ', lines ' / ', <speaker>); the
English is one paragraph a page, pages joined by ' || '; merge wraps it (pages.build_en) into `en` and keeps the
paragraphs in `pages`. Side tables: English in script syntax, same control codes as the JP.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grid  # noqa: E402
import pages  # noqa: E402
from font_en import text_px  # noqa: E402
from tag_font import WIDE_CELLS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]")
# engine B row break (the English places its own, 28 cells a row) and FF05 "print instantly to the next FFxx" (the
# English repeats it after each {FF0E:n} cell jump of a VWF layout row, ceremony 1DEFD1); 00AB = 岬 (unread kanji)
FREE = {"{FF01}", "{FF05}", "[00AB]"}


def free_token(t):
    """FREE codes and `[hhhh]` glyph words (0x0060-0x04FF: a kanji the table prints as a code, or a stray glyph
    word such as 05E8A0's [011E]): the English may drop or keep them."""
    # {FF0E:n} = engine B "advance the cursor n cells" (docs/re/text.md): layout, like {FF01}
    return t in FREE or t.startswith("{FF0E:") or (t.startswith("[") and 0x60 <= int(t[1:5], 16) <= 0x4FF)
VARIABLE = r"\{(?:FF2B|FF2C)\}"
# Glossary "Honorifics" (D1): every honorific after a name or name variable keeps its suffix.
HONORIFICS = {"さん": "-san", "様": "-sama", "さま": "-sama", "殿": "-dono", "どの": "-dono", "ちゃん": "-chan",
              "くん": "-kun"}
NOT_NAMES = {"バア", "ジイ", "オバ", "オレ", "ハンター", "コソドロ"}   # old lady, old man, "Me-sama": not honorifics
# Side-table budgets (docs/re/vwf.md width gate): ("px", n) = pixels, C1 VWF field (cells x 8); ("ch", n) = one
# character a cell; ("row", n) = engine B rows of n cells broken by {FF01}.
LIMITS = {"items": ("px", 80), "classes": ("px", 80), "spells": ("px", 80), "unit_names": ("px", 48),
          "unit_titles": ("px", 128), "constellations": ("px", 40), "orders": ("px", 64),
          "town_menu": ("px", 40),
          # location label and name tag (C2:5641, 6 cells): English pre-rendered by tools/tag_font.py (D8); the label
          # is drawn 14 cells wide from bank $FF (D20, asm/loc_label.asm, tag_font.WIDE_CELLS)
          "locations": ("px", 112), "speakers": ("px", 48), "move_prompt": ("px", 96),
          "ceremony": ("row", 28), "short_strings": ("row", 28), "descriptions": ("desc", 128)}
EXACT = {"objectives"}
# Shop dialogue (short_strings 1AF585..1AFDC2) draws in the portrait box: 20 cells a row, measured 2026-11-23
# (`work/qa/w_shopruler`: a ruler row wraps after cell 20 and pushes the Buy/Sell/Quit row back to row 1).
# Rows count {FF0E:n} as n cells and each {FF06} variable at its longest English value.
SHOP = (0x1AF585, 0x1AFDC2, 20)
SHOP_VARS = {"48CD": 16, "48E3": 16, "48F9": 5, "4905": 9, "F569": 16}   # item, item, price, unit name, greeting


# Engine B rows elsewhere: {FF06} variables of known longest English width (others count 0). ED2D = guardian spirit
# (ceremony 1DED5B.., longest "Aphrodite"); 4D1B = hero name (name-entry buffer, 6 cells).
ROW_VARS = {"ED2D": 9, "4D1B": 6}


# Description box (position table C3:C63C, camp/shop Select and spell lists): 2 rows of 16 cells = 128 px a row,
# 32 cells in all; asm/vwf.asm EngBGlyph counts its cells by ink. An {FF01} goes to the next 16-cell row, so a row
# before one must end inside cell 15 (<= 120 px): a full row puts the counter on row 2 and the {FF01} wraps to row 1
# over the text (user report rom/bounty_item_desc.mss, `work/qa/fix_desc_*`). Pages end in {FF03}, shared pieces
# in {FF07}; a page that opens with a call to one of the one-row pieces (E52E/E53C/E54A) has one row left.
DESC_ROW, DESC_ROWS = 128, 2
DESC_PIECES = re.compile(r"\{FF06:(?:E52E|E53C|E54A):00CE\}")


def desc_problems(en, row_px=DESC_ROW):
    out = []
    for seg in re.split(r"\{FF07\}|\{FF03\}", en):
        lead = 1 if DESC_PIECES.match(seg) else 0
        rows = [TOKEN.sub("", r) for r in seg.split("{FF01}")]
        for i, r in enumerate(rows):
            lim = row_px - 8 if i < len(rows) - 1 else row_px
            if text_px(r) > lim:
                out.append(f"description row over {lim} px ({text_px(r)}): {r!r}")
        if lead + sum(1 for r in rows if r) > DESC_ROWS:
            out.append(f"more than {DESC_ROWS} description rows on a page: {TOKEN.sub('', seg)!r}")
    return out


def shop_row_cells(row, variables=SHOP_VARS):
    n = sum(int(k, 16) for k in re.findall(r"\{FF0E:([0-9A-F]{4})\}", row))
    n += sum(variables.get(k, 0) for k in re.findall(r"\{FF06:([0-9A-F]{4})", row))
    return n + len(TOKEN.sub("", row))
NAMES = {"{FF1F}": "HERO", "{FF28}": "FF28", "{FF31}": "FF31"}


def docs():
    for path in sorted(SCRIPT.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        yield path, doc, doc


def is_master(entry):
    return "slots" in entry


def needs_english(entry):
    """Text with at least one kana, kanji or letter in it (a run of codes and spacers is layout data)."""
    letters = [c for c in TOKEN.sub("", entry.get("jp", "")) if kind(c) != "other" or c.isalnum()]
    return entry.get("kind", "text") == "text" and bool(letters) and not entry.get("en")


def group_of(entry):
    return entry["id"]


def entry_key(entry):
    return entry["id"]


def file_of(entry):
    return entry.get("_file", "")


def form_of(entry):
    return "dlg" if is_master(entry) else file_of(entry)


def limit_label(entry):
    if is_master(entry):
        return f"{pages.LINE_PX}px x{pages.LINES}"
    lim = LIMITS.get(file_of(entry))
    if not lim:
        return f"{entry.get('cells') or entry['width']} cells" if entry.get("width") else ""
    return f"{lim[1]}{lim[0]}"


def jp_column(entry):
    if is_master(entry):
        return pages.jp_view(entry["jp"], NAMES)
    return entry["jp"].replace("\n", "\\n")


def speaker_of(entry):
    m = re.match(r"\{spk\}([^\n]*)", entry["jp"]) if is_master(entry) else None
    return pages.speaker(m.group(0), NAMES) if m else ""


def grid_codes(entry, text):
    """C1 grid strings (tools/grid.py): drop the cursor codes, glyph words (< 0x0F00, e.g. [0001] ん) and one-letter
    English words ([0F41] = an unpacked "A": the name-entry keyboards, D17) before the control-code comparison: the
    English places its own cells."""
    if file_of(entry) not in grid.GRID_FILES:
        return text
    return re.sub(r"\[0[0-9A-E][0-9A-F]{2}\]|\[0F[2-7][0-9A-F]\]", "", grid.CURSOR.sub("", text))


def width_problems(entry, en):
    if file_of(entry) in grid.GRID_FILES and entry.get("width"):
        return grid.problems(en, entry.get("cells") or entry["width"])   # cells: widened copy (script_text)
    if file_of(entry) in EXACT:     # repacked in place, entries addressed by pointers: one char a word, same count
        n_jp, n_en = len(TOKEN.sub("", entry["jp"])), len(TOKEN.sub("", en))
        return [] if n_en == n_jp else [f"{n_en} characters, the slot holds exactly {n_jp} (pad with spaces)"]
    lim = LIMITS.get(file_of(entry))
    if is_master(entry) or not lim:
        return []
    kind, n = lim
    if kind == "px":
        cells = WIDE_CELLS.get(file_of(entry)) or entry.get("width") or n // 8
        plain = TOKEN.sub("", en)
        if text_px(plain) > cells * 8 or len(plain) > 2 * cells:
            return [f"over {cells * 8} px ({text_px(plain)})"]
    elif kind == "desc":
        return desc_problems(en, n)
    elif kind == "ch":
        if len(TOKEN.sub("", en)) > (entry.get("width") or n):
            return [f"over {entry.get('width') or n} characters"]
    elif kind == "row":
        rows = re.split(r"\{FF01\}|\{FFFF\}", en)
        if file_of(entry) == "short_strings" and SHOP[0] <= int(entry["id"], 16) <= SHOP[1]:
            out = [f"shop row over {SHOP[2]} cells ({shop_row_cells(r)}): {TOKEN.sub('', r)!r}"
                   for r in rows if shop_row_cells(r) > SHOP[2]]
            # a full row wraps by itself, so an {FF01} after it skips a row: the Yes/No of 1AFD1A landed on row 1
            # over the price (`work/qa/w_shopx`, session n)
            out += [f"shop row of {SHOP[2]} cells before {{FF01}} wraps twice: {TOKEN.sub('', r)!r}"
                    for r in rows[:-1] if shop_row_cells(r) == SHOP[2]]
            jp_rows = entry["jp"].split("{FF01}")    # a JP row past 20 cells wraps on its own: one more row
            if en.count("{FF01}") > len(jp_rows) - 1 + sum(shop_row_cells(r) > SHOP[2] for r in jp_rows):
                out.append("more {FF01} rows than the JP shows (the shop box holds 3 rows)")
            return out
        if any(shop_row_cells(r, ROW_VARS) > n for r in rows):
            return [f"a row over {n} characters (break rows with {{FF01}})"]
        # a full row wraps by itself, so the {FF01} after it lands on a third row and overwrites: "Guardian spirit:
        # Aphrodite" then "Dost thou accept it?" drew on one row (`work/qa/w_aphro2`, 2026-11-23)
        return [f"row of {n} cells before {{FF01}} wraps twice: {TOKEN.sub('', r)!r}"
                for r in rows[:-1] if shop_row_cells(r, ROW_VARS) == n]
    return []


# JP font, 8 px a cell; あ/ア: the name-entry keyboards' page keys (D13)
GRID_GLYPHS = set("　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ０１２３４５６７８９あア")


def encodable(char):
    return " " <= char <= "~" and char not in "{}[]"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    jp = jp.replace(" / ", "").replace("　", "")
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


KEEP_JP = SCRIPT / "keep_jp.txt"
SPEAKER_TAGS = SCRIPT / "speaker_tags.tsv"


def keep_problems(entries):
    """Text entries with jp and no en must be in script/keep_jp.txt (id TAB reason); listed ids must still need it."""
    keep = {}
    for n, line in enumerate(KEEP_JP.read_text(encoding="utf-8").splitlines() if KEEP_JP.exists() else (), 1):
        if line.strip() and not line.startswith("#"):
            eid, _, why = line.partition("\t")
            if not why.strip():
                return [f"keep_jp.txt:{n}: want ID<TAB>reason"]
            keep[eid.strip()] = why
    out = [f"{i}: Japanese with no English and not in script/keep_jp.txt" for i, e in entries.items()
           if needs_english(e) and i not in keep]
    return out + [f"keep_jp.txt: {i} " + ("is gone" if i not in entries else "needs no keep line (has English)")
                  for i in keep if i not in entries or not needs_english(entries[i])]


def glossary_tags():
    """[(JP forms, allowed tag forms)]: a row's EN forms plus `tag "X"` forms named in its notes (D8 short tags)."""
    rows = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines() if GLOSSARY.exists() else ():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 4 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            ens = [x.strip() for x in cells[1].split("/")] + re.findall(r'tag "([^"]+)"', cells[3])
            rows.append(([x.strip() for x in cells[0].split("/")], ens))
    return rows


def tag_problems(terms=None):
    """Each speaker tag whose JP name holds a glossary term must use one of that row's EN or tag forms."""
    out = []
    for n, line in enumerate(SPEAKER_TAGS.read_text(encoding="utf-8").splitlines() if SPEAKER_TAGS.exists() else (), 1):
        if not line.strip() or line.startswith("#"):
            continue
        jp, _, en = line.partition("\t")
        for jps, ens in glossary_tags():
            if any(has_term(jp, j) for j in jps) and not any(e.lower() in en.lower() for e in ens if e):
                out.append(f"speaker_tags.tsv:{n}: {jp} -> {en!r}: glossary wants {' / '.join(ens)}"
                           ' (or add `tag "X"` to the row\'s notes, D8)')
    return out


def master_tokens(text):
    return Counter(t for t in pages.TOKEN.findall(text) if t in pages.INLINE_PX)


def problems(entry, en, terms):
    """Every rule, on one entry's English (master: the page paragraphs)."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    raw = is_master(entry) and pages.split(jp)[0]
    plain = TOKEN.sub("", en.replace("\\n", "").replace("||", ""))
    jp_font = set(TOKEN.sub("", jp)) | (GRID_GLYPHS if file_of(entry) in grid.GRID_FILES else set())
    if bad := sorted({c for c in plain if not encodable(c) and c not in jp_font}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    if is_master(entry) and not raw:
        jp_pages = "".join(it[1] + "".join(it[2]) for it in pages.split(jp)[1] if it[0] == "page")
        if master_tokens(jp_pages) != master_tokens(en):
            out.append(f"name/number words differ: JP {dict(master_tokens(jp_pages))} EN {dict(master_tokens(en))}")
        built, probs = pages.build_en(jp, en)
        out += probs
    else:
        want = Counter(t for t in TOKEN.findall(grid_codes(entry, jp)) if not free_token(t))
        have = Counter(t for t in TOKEN.findall(grid_codes(entry, en)) if not free_token(t))
        if want != have:
            out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. {FF2B}")')
    jp_plain = TOKEN.sub("", re.sub(r"\{spk\}[^\n]*\n", "\n", jp))   # speaker tags are mapped in phase 7 (D8)
    en_terms = " ".join(TOKEN.sub(" ", en).replace("\\n", " ").split()).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    jp_names = re.sub(r"\{spk\}[^\n]*\n", "\n", jp)   # keeps {hero}/{FF31}: "{hero}どの" is an honorific too
    for jp_form, en_form in HONORIFICS.items():
        named = [m for m in re.findall(r"(\{hero\}|\{FF1F\}|\{FF31\}|[ァ-ヺー°]+)" + jp_form, jp_names)
                 if m not in NOT_NAMES]
        if named and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form} (or note it in UNSURE if it is not an honorific)")
    if re.search(r"\{(?:hero|FF1F|FF31)\}'s\b", en):
        out.append("\"'s\" after a name variable (write \"the sword of {hero}\" or rephrase)")
    return out + width_problems(entry, en) + widows(entry, en)


def index():
    result = {}
    for path, _, entries in docs():
        for e in entries:
            e["_file"] = path.stem
            if entry_key(e) in result:
                raise ValueError(f"duplicate batch key {entry_key(e)!r}")
            result[entry_key(e)] = e
    return result


def authored(entry):
    """The English as translated: master page paragraphs, else en."""
    return entry.get("pages") or entry.get("en", "") if is_master(entry) else entry.get("en", "")


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def selected(entry, only):
    return not only or (only == "master" and is_master(entry)) or (only == "side" and not is_master(entry)) \
        or file_of(entry) == only


def split(size, only=None):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    entries = index()
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for e in entries.values():
        if needs_english(e) and entry_key(e) not in taken and selected(e, only):
            groups.setdefault((file_of(e), group_of(e)), []).append(e)
    batches, cur, chars, cur_file = [], [], 0, None
    for (fname, _), group in groups.items():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES or fname != cur_file):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
        cur_file = fname
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t{speaker_of(e)}\t{form_of(e)}\t{limit_label(e)}\t{jp_column(e)}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def widows(entry, en):
    """Master pages whose wrap leaves a one-line box starting mid-sentence (pages.widows)."""
    if not is_master(entry):
        return []
    return ([f"widow box {w}" for w in pages.widows(entry["jp"], en)]
            + [f"stub last line {s}" for s in pages.stubs(entry["jp"], en)])


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    got = [r[0] for r in rows]
    if got != want:
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def page_view(entry, n):
    """(JP page n as one line, English page n) of a merged master entry, n from 1."""
    jp = pages.jp_view(entry["jp"], NAMES).split(" ‖ ")
    en = [p.strip() for p in entry["pages"].split("||")]
    return jp[n - 1], en[n - 1]


def repage(name, *srcs):
    """Fit-pass input: rows `id<TAB>page<TAB>new English page` (pages from 1) -> work/tl/NAME.tsv + NAME.out.tsv
    with each entry's full page paragraphs, the named pages replaced (a later file's row wins: retries go in a
    second file); then `check NAME`, `merge NAME --overwrite`."""
    entries = index()
    new = {}
    rows = [row for src in srcs for row in read_tsv(Path(src))]
    for row in rows:
        eid, n, text = row[0], int(row[1]), "\t".join(row[2:])
        e = entries[eid]
        cur = new.get(eid) or [p.strip() for p in e["pages"].split("||")]
        cur[n - 1] = text.strip()
        new[eid] = cur
    ids = list(new)
    (TL / f"{name}.tsv").write_text("".join(f"{i}\t{speaker_of(entries[i])}\t{form_of(entries[i])}\t"
                                            f"{limit_label(entries[i])}\t{jp_column(entries[i])}\n" for i in ids),
                                    encoding="utf-8", newline="\n")
    (TL / f"{name}.out.tsv").write_text("".join(f"{i}\t{pages.SEP.join(new[i])}\n" for i in ids),
                                        encoding="utf-8", newline="\n")
    print(f"{name}: {len(ids)} entries, {len(rows)} page rows")


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e.get("en") and authored(e) != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {authored(e)!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            src = new.get(entry_key(e))
            if src is None or authored(e) == src and e.get("en"):
                continue
            if is_master(e) and not pages.split(e["jp"])[0]:
                e["en"], _ = pages.build_en(e["jp"], src)
                e["pages"] = src
            else:
                e["en"] = src.replace("\\n", "\n") if is_master(e) else src
            touched = True
            changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        size = int(args[args.index("--size") + 1]) if "--size" in args else 3500
        return split(size, args[args.index("--only") + 1] if "--only" in args else None)
    if cmd == "zip":   # zip bNNN LINES.txt: one English line per batch row, in order -> bNNN.out.tsv
        ids = [r[0] for r in read_tsv(TL / f"{args[0]}.tsv")]
        lines = Path(args[1]).read_text(encoding="utf-8").rstrip("\n").split("\n")
        if len(lines) != len(ids):
            sys.exit(f"{len(lines)} lines for {len(ids)} ids")
        (TL / f"{args[0]}.out.tsv").write_text("".join(f"{i}\t{t}\n" for i, t in zip(ids, lines)), encoding="utf-8",
                                               newline="\n")
        return 0
    if cmd == "rewrap":   # after a pages.py change: rebuild `en` of every merged master entry from its `pages`
        changed = 0
        for path, doc, entries in docs():
            touched = False
            for e in entries:
                if is_master(e) and e.get("pages") and not pages.split(e["jp"])[0]:
                    en, _ = pages.build_en(e["jp"], e["pages"])
                    if en is not None and en != e.get("en"):
                        e["en"], touched = en, True
                        changed += 1
            if touched:
                path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"rewrap: {changed} entries changed")
        return 0
    if cmd == "repage":   # repage NAME FIX.tsv [RETRY.tsv ...] (id, page, English page) -> NAME.tsv/.out.tsv
        return repage(args[0], *args[1:])
    if cmd == "fit":      # fit '"quoted page"' ...: dry-run wrap, boxes of 3 lines with pixel widths
        for text in args:
            q = text.startswith('"') and text.endswith('"')
            lines = pages.wrap(text.strip('"') if q else text, "「" if q else "", " " if q else "",
                               pages.px("」") if q else 0)
            for k, ln in enumerate(lines):
                print(("--\n" if k and k % pages.LINES == 0 else "") + f"{pages.px(ln):4d} {ln}")
            print("==")
        return 0
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "widows":   # widows [--limit N]: id, page, JP page, English page of every widow box (fit-pass input)
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 10 ** 6
        rows = [(i, w) for i, e in entries.items() if is_master(e) and e.get("pages")
                for w in pages.widows(e["jp"], e["pages"])]
        for i, w in rows[:limit]:
            n = int(w.split(":")[0].split()[1])
            jp, en = page_view(entries[i], n)
            print(f"{i}\t{n}\t{jp}\t{en}")
        print(f"{len(rows)} widow boxes in {len({i for i, _ in rows})} entries", file=sys.stderr)
        return 0
    if cmd == "check" and not names:
        bad = [f"{i}: {p}" for i, e in entries.items() if e.get("en") for p in problems(e, authored(e), terms)]
        bad += keep_problems(entries) + tag_problems(terms)
        print(f"{len(entries)} entries, {sum(1 for e in entries.values() if e.get('en'))} in English, "
              f"{len(bad)} problems (widow boxes count: `batches.py widows` lists them for a fit pass)")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
