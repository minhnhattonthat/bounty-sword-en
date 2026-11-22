"""tools/batches.py lint rules added after the phase 7 review: keep-list for Japanese left on purpose, speaker tags
against the glossary."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def test_untranslated_entry_outside_the_keep_list_fails(tmp_path, monkeypatch):
    keep = tmp_path / "keep_jp.txt"
    keep.write_text("# comment\nAAA\tjunk record\n", encoding="utf-8")
    monkeypatch.setattr(batches, "KEEP_JP", keep)
    entries = {"AAA": {"id": "AAA", "jp": "あいう", "en": ""}, "BBB": {"id": "BBB", "jp": "かきく", "en": ""},
               "CCC": {"id": "CCC", "jp": "さしす", "en": "Sasu"}}
    probs = batches.keep_problems(entries)
    assert probs == ["BBB: Japanese with no English and not in script/keep_jp.txt"]
    keep.write_text("AAA\tjunk\nBBB\tjunk\nCCC\tstale\n", encoding="utf-8")
    assert batches.keep_problems(entries) == ["keep_jp.txt: CCC needs no keep line (has English)"]


def test_speaker_tag_must_use_a_glossary_form(tmp_path, monkeypatch):
    gl = tmp_path / "glossary.md"
    gl.write_text("| JP | EN | max | notes | Avoid |\n|---|---|---|---|---|\n"
                  '| スカルナイト | Skull Knight | | speaker tag: tag "Skull" | |\n', encoding="utf-8")
    tags = tmp_path / "speaker_tags.tsv"
    monkeypatch.setattr(batches, "GLOSSARY", gl)
    monkeypatch.setattr(batches, "SPEAKER_TAGS", tags)
    tags.write_text("スカルナイト\tSkull\nロジャー\tRoger\n", encoding="utf-8")
    assert batches.tag_problems() == []
    tags.write_text("スカルナイト\tSkeleton\n", encoding="utf-8")
    assert len(batches.tag_problems()) == 1


def test_shop_rows_fit_the_20_cell_portrait_box():
    entry = {"id": "1AF7FC", "_file": "short_strings", "jp": "「さっそく装備しますか？」{FF01}{FF0E:0006}はい"}
    assert batches.width_problems(entry, '"Equip it now?"{FF01}{FF0E:0006}Yes') == []
    assert batches.width_problems(entry, '"Will you equip it now?"{FF01}{FF0E:0006}Yes')       # 24 cells
    assert batches.width_problems(entry, '"Equip it{FF01}now?"{FF01}{FF0E:0006}Yes')          # a 4th row
    # a full 20-cell row wraps by itself, so its {FF01} skips a row (Yes/No drew over row 1, 1AFD1A)
    assert batches.width_problems(entry, '"Shall I equip it??"{FF01}{FF0E:0006}Yes')          # 20 then FF01
    assert batches.width_problems(entry, '"Shall I equip it?"{FF01}{FF0E:0006}Yes') == []     # 19
    # variables count at their longest English value: item 16, price 5
    assert batches.shop_row_cells('"{FF06:48CD:007E}{FF0E:0003}{FF06:48F9:007E}G"') == 1 + 16 + 3 + 5 + 2


def test_engine_b_yes_no_keeps_the_cursor_cells():
    """Engine B choices draw one char a cell and put the cursor from a fixed table (1AF842: x 0x60 / 0x88), so "No"
    must start on the cell いいえ did: len(Yes) + gap == len(はい) + gap_jp (a 3-cell gap left No 8 px off its cursor)."""
    import re
    pat = re.compile(r"(\S+?)\{FF0E:([0-9A-F]{4})\}(\{FF05\})?(No|いいえ)")
    seen = 0
    for e in batches.index().values():
        jp, en = pat.search(e.get("jp") or ""), pat.search(e.get("en") or "")
        if not (jp and en and jp.group(1).endswith("はい")):
            continue
        seen += 1
        assert len("Yes") + int(en.group(2), 16) == len("はい") + int(jp.group(2), 16), e["id"]
    assert seen >= 8


def test_repo_lint_has_no_keep_or_tag_problems():
    assert batches.keep_problems(batches.index()) == []
    assert batches.tag_problems() == []
