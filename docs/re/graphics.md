# Graphics-text survey (phase 1, IN PROGRESS)

Rule (skill `references/graphics.md` §Survey): every Japanese-on-screen element is either a known string or a row
here. Tour so far: cold boot -> title -> file menu -> new game -> ceremony -> name entry -> first town scene -> chapter
card -> first map (`work/qa/orig_boot`, `orig_new`, `orig_g1`). Battle, shop, status/unit menus, game over, ending
and credits are not toured yet (needs the phase-2 debug tool).

| Screen | Element | Japanese? | Source (first guess) | State |
|---|---|---|---|---|
| Boot | PIONEER LDC logo, staff cards (Tenmi Qual, Kohei Tanaka) | no, English | tiles | ok |
| Title | BOUNTY SWORD logo, © 1995 PIONEER LDC / ITL line | no, English | tiles | ok (D5: keep) |
| File menu | ファイル / 最初から / ロード / コピー / 消去 / 未使用 | yes | font (C1 menu strings) | text, not graphics |
| Ceremony | dialogue box, はい/いいえ | yes | font (engine B) | text |
| Ceremony | stat sheet (unit stats grid) | yes | font? | check in phase 5 marker build |
| Name entry | kana keyboard grid, カナ 英字 終わり, NAME label | yes (NAME is English) | font-drawn grid or tilemap: unverified | **check** |
| Town scene | portrait name plate | yes | font, drawn by C2:565E into $7E:AC00 | text |
| Town scene | speech bubble frame | no | tiles | ok |
| Chapter card | 第1話 『…』 | yes | font? unverified | **check** (dump VRAM) |

## Static sweep (not done)

`tools/gfx_sweep.py OUT --bpp 2|4 [--from --to --cols --rows]` renders the ROM with offset labels and never skips a
range. A whole-ROM 512 KB sheet is unreadable (tried: `work/sweep/sweep4_000000.png`): use 32-64 KB per sheet
(`--rows 16..32`) and only over graphics-looking banks, read in chunks. Graphics are raw or plane-expanded in ROM
(`docs/re/rom.md`), so a sweep of raw ROM is meaningful.
