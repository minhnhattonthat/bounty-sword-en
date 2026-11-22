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


def test_repo_lint_has_no_keep_or_tag_problems():
    assert batches.keep_problems(batches.index()) == []
    assert batches.tag_problems() == []
