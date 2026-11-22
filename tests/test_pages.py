"""tools/pages.py: English pages wrap into the game's box shape and keep the message skeleton."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pages  # noqa: E402
from script_text import TextCodec  # noqa: E402

JP = "{spk}{FF28}\n「ここは　イーストエンドよ\n　まだ　この地は　クリアしてないわ」\n{next}\n「でも　逃げてよかったの？」\n"


def test_view_shows_pages_and_speaker():
    assert pages.jp_view(JP, {"{FF28}": "FF28"}) == ("<FF28> 「ここは　イーストエンドよ / まだ　この地は　クリアしてないわ」"
                                                    " ‖ 「でも　逃げてよかったの？」")


def test_build_keeps_skeleton_and_splits_long_pages():
    long = '"' + " ".join(["word"] * 60) + '"'
    en, probs = pages.build_en(JP, f'"This is East End." || {long}')
    assert not probs
    lines = en.split("\n")
    assert lines[0] == "{spk}{FF28}" and lines[1] == "「This is East End.」" and lines[-1] == ""
    boxes = en.split("{next}")
    assert len(boxes) > 2                                   # the long page became several boxes
    for box in boxes[1:]:
        text = [ln for ln in box.strip("\n").split("\n") if ln]
        assert 1 <= len(text) <= pages.LINES
        assert text[0].startswith("「") and text[-1].endswith("」")
        assert all(pages.px(ln) <= pages.LINE_PX + 4 for ln in text)
    TextCodec(True).encode(en)                              # encodable as master text


def test_choice_list_keeps_cursor_indent_but_narration_does_not():
    menu = "{spk}{FF28}\n「何？」\n{next}\n　連邦の情報\n　秘密の情報\n{FF14:00C3}{end}\n"
    en, probs = pages.build_en(menu, '"What?" || A\\nB')
    assert not probs and "\n　A\n　B\n{FF14:00C3}" in en
    poem = "{spk}{FF28}\n　地に　やみが\n　あふれ\n{next}\n「ね？」\n"
    en, probs = pages.build_en(poem, 'Darkness. || "Right?"')
    assert not probs and "\nDarkness.\n" in en


def test_page_count_and_quotes_are_checked():
    assert pages.build_en(JP, '"One page only."')[1]
    assert pages.build_en(JP, 'No quotes. || "Fine."')[1]


def test_every_master_message_has_a_page_view():
    for path in sorted((ROOT / "script").glob("master_*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            raw, items = pages.split(e["jp"])
            assert "\n".join(it[1] if it[0] == "line" else "\n".join(
                [it[1] + it[2][0]] + it[2][1:]) for it in items) == e["jp"]
