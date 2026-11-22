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

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{4}\]")
FREE = {"{FF01}", "[00AB]"}  # engine B row break (the English places its own, 28 cells a row); 00AB = 岬 (unread kanji)


def free_token(t):
    """FREE codes and `[hhhh]` glyph words (0x0060-0x04FF: a kanji the table prints as a code, or a stray glyph
    word such as 05E8A0's [011E]): the English may drop or keep them."""
    return t in FREE or (t.startswith("[") and 0x60 <= int(t[1:5], 16) <= 0x4FF)
VARIABLE = r"\{(?:FF2B|FF2C)\}"
# Glossary "Honorifics" (D1): every honorific after a name or name variable keeps its suffix.
HONORIFICS = {"さん": "-san", "様": "-sama", "さま": "-sama", "殿": "-dono", "どの": "-dono", "ちゃん": "-chan",
              "くん": "-kun"}
NOT_NAMES = {"バア", "ジイ", "オバ", "オレ", "ハンター", "コソドロ"}   # old lady, old man, "Me-sama": not honorifics
# Side-table budgets (docs/re/vwf.md width gate): ("px", n) = pixels, C1 VWF field (cells x 8); ("ch", n) = one
# character a cell; ("row", n) = engine B rows of n cells broken by {FF01}.
LIMITS = {"items": ("px", 80), "classes": ("px", 80), "spells": ("px", 80), "unit_names": ("px", 48),
          "unit_titles": ("px", 128), "constellations": ("px", 40), "orders": ("px", 64),
          # location label (C0:E1B1, 10 cells) and name tag (C2:5641, 6 cells) draw one char a cell today: phase 7
          # packs two letters a cell there like C1Run (decision D8), so they get the pair budget too.
          "locations": ("px", 80), "speakers": ("px", 48),
          "ceremony": ("row", 28), "short_strings": ("row", 28), "descriptions": ("row", 28)}
EXACT = {"objectives"}
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
        return f"{entry['width']} cells" if entry.get("width") else ""
    return f"{lim[1]}{lim[0]}"


def jp_column(entry):
    if is_master(entry):
        return pages.jp_view(entry["jp"], NAMES)
    return entry["jp"].replace("\n", "\\n")


def speaker_of(entry):
    m = re.match(r"\{spk\}([^\n]*)", entry["jp"]) if is_master(entry) else None
    return pages.speaker(m.group(0), NAMES) if m else ""


def grid_codes(entry, text):
    """C1 grid strings (tools/grid.py): drop the cursor codes and glyph words (< 0x0F00, e.g. [0001] ん) before the
    control-code comparison: the English places its own cells."""
    if file_of(entry) not in grid.GRID_FILES:
        return text
    return re.sub(r"\[0[0-9A-E][0-9A-F]{2}\]", "", grid.CURSOR.sub("", text))


def width_problems(entry, en):
    if file_of(entry) in grid.GRID_FILES and entry.get("width"):
        return grid.problems(en, entry["width"])
    if file_of(entry) in EXACT:     # repacked in place, entries addressed by pointers: one char a word, same count
        n_jp, n_en = len(TOKEN.sub("", entry["jp"])), len(TOKEN.sub("", en))
        return [] if n_en == n_jp else [f"{n_en} characters, the slot holds exactly {n_jp} (pad with spaces)"]
    lim = LIMITS.get(file_of(entry))
    if is_master(entry) or not lim:
        return []
    kind, n = lim
    if kind == "px":
        cells = entry.get("width") or n // 8
        plain = TOKEN.sub("", en)
        if text_px(plain) > cells * 8 or len(plain) > 2 * cells:
            return [f"over {cells * 8} px ({text_px(plain)})"]
    elif kind == "ch":
        if len(TOKEN.sub("", en)) > (entry.get("width") or n):
            return [f"over {entry.get('width') or n} characters"]
    elif kind == "row":
        rows = re.split(r"\{FF01\}|\{FFFF\}", en)
        if any(len(TOKEN.sub("", r)) > n for r in rows):
            return [f"a row over {n} characters (break rows with {{FF01}})"]
    return []


GRID_GLYPHS = set("　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ０１２３４５６７８９")   # JP font, 8 px a cell


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
    return out + width_problems(entry, en)


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
    return [f"widow box {w}" for w in pages.widows(entry["jp"], en)] if is_master(entry) else []


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
            bad += [f"{eid}: {p}" for p in problems(entries[eid], en, terms) + widows(entries[eid], en)]
    return bad, dict(rows)


def page_view(entry, n):
    """(JP page n as one line, English page n) of a merged master entry, n from 1."""
    jp = pages.jp_view(entry["jp"], NAMES).split(" ‖ ")
    en = [p.strip() for p in entry["pages"].split("||")]
    return jp[n - 1], en[n - 1]


def repage(name, src):
    """Fit-pass input: rows `id<TAB>page<TAB>new English page` (pages from 1) -> work/tl/NAME.tsv + NAME.out.tsv
    with each entry's full page paragraphs, the named pages replaced; then `check NAME`, `merge NAME --overwrite`."""
    entries = index()
    new = {}
    for row in read_tsv(Path(src)):
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
    print(f"{name}: {len(ids)} entries, {sum(1 for _ in read_tsv(Path(src)))} pages replaced")


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
    if cmd == "repage":   # repage NAME FIX.tsv (id, page, English page) -> NAME.tsv/.out.tsv
        return repage(args[0], args[1])
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
        wid = sum(len(widows(e, authored(e))) for e in entries.values() if e.get("pages"))
        print(f"{len(entries)} entries, {sum(1 for e in entries.values() if e.get('en'))} in English, "
              f"{len(bad)} problems, {wid} widow boxes (warning; `batches.py widows` lists them for the fit pass)")
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
