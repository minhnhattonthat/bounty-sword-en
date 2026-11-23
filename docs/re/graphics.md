# Graphics-text survey (phase 1 done; the phase-5 marker tour and phase-8 warps re-check it)

Rule (skill `references/graphics.md` §Survey): every Japanese-on-screen element is either a known string or a row
here. Tour so far: cold boot -> title -> file menu -> new game -> ceremony -> name entry -> first town scene ->
chapter card -> prologue narration -> first map (`work/qa/orig_boot`, `orig_new`, `orig_g1`, `card`). Battle, shop,
status/unit menus, game over, ending and credits are not toured yet (phase-2 debug tool).

| Screen | Element | Japanese? | Source | State |
|---|---|---|---|---|
| Boot | PIONEER LDC logo, staff cards (Tenmi Qual, Kohei Tanaka) | no, English | tiles | ok |
| Title | BOUNTY SWORD logo, © 1995 PIONEER LDC / ITL line | no, English | tiles | ok (D5: keep) |
| File menu | ファイル / 最初から / ロード / コピー / 消去 / 未使用 | yes | font, C1 menu strings | text |
| Ceremony | dialogue box, はい/いいえ | yes | font (engine B) | text |
| Ceremony | stat sheet (unit stats grid) | yes | font? | check in the phase-5 marker build |
| Name entry | kana grid, カナ / 英字 / 終わり | yes | font: the grid is the C1 string at 0x1C285 (あいうえおか…), カナ…終わり follows it. The typed character is the grid word at the cursor index (C6:F139, page table C6:F16A); 96 cells = 6 groups of 16 words, each 3 rows of 5 + 1 unused (row k at word (k//3)*16+(k%3)*5; screen blocks of 5 rows). Cursor start: script op `06 6e0d00 nnnn` at 0x6E368 / 0x6EF2A. English since D17 | text (verified by string) |
| Name entry | NAME label | no, English | tiles | ok |
| Town scene | portrait name plate | yes | font, drawn by `C2:565E` into `$7E:AC00` | text |
| Town scene | speech bubble frame | no | tiles | ok |
| **Chapter card** | 第1部 『迫り来る恐怖』 (and 第2部『遥かな地で』, 第3部『魔の中枢へ』) | **yes** | **graphics**: 16x16 2bpp glyphs, raw, ROM 0x18449A-0x184A99 (第 １ ２ ３ 部 迫 り 来 る 恐 怖 遥 か な 地 で ・ 魔 の 中 枢 へ), loaded to VRAM $8000 (BG3) and placed by a tilemap. Verified: `vramfind.py --fmt snes2` on the card's VRAM dump (`work/qa/card/ppu_000450.*`), BG3 render `work/qa/card/layers.png`. Text search finds no 迫り来る string. | **done** (session q): the block is really 93 linear 2bpp tiles ($5D0 at $D8:449A -> VRAM $8000) + 3 tilemaps ($140 each at $D8:4A6A/4BAA/4CEA -> VRAM $8800), loaded by DMA records C1:5153.. (`01 src24 vram size size`); `tools/card_gfx.py` redraws all three in the project font into the same space (66 tiles). In game: part 1 from `work/states/ng_town.mss` (f1710), parts 2/3 with map 1 swapped in a test copy: `work/qa/part_cards.png` |
| Prologue | narration on brown screen (イーストエンドの…) | yes | font (master dialogue msg 0) | text |
| Location label | map name (ラインメタル…), 10 cells | yes | font via `C0:E1B1`, table 0x0CD7B | text |
| Battle effects | CRITICAL, MISS, ATK UP, DEF UP, LEVEL UP, digits | no, English | sprite tiles 0x091000, 0x0A0000 | ok |
| UI | OFF/ON, HP S/G LV EX, arrows, digits | no, English | 4bpp tiles 0x18549A | ok |
| Font | 8x16 kana/kanji | (it is the font) | 0x2B2D8C | text work (phase 5) |

## Static sweep (done)

1. `tools/gfx_map.py > work/sweep/gfxmap.txt` classes every 4 KB block: fill, text/words (16-bit text, either
   byte parity), GFX+P (tile-structured, tiles start at byte phase P), other (code/data, scores like random).
   Phase matters: the card glyphs sit at 0x18449A and read as noise from an aligned start.
2. `tools/gfx_sweep_map.py work/sweep/gfxmap.txt work/sweep/m` renders the 271 GFX blocks (1,084 KB) at their
   phase, 2bpp, zoom 2, 8 blocks per sheet: 34 sheets `work/sweep/m/map_*.png`. It prints every non-GFX run it
   skips (88 runs: code, text, fill).
3. All 34 sheets read (2026-11-22, one pass by the phase-1 worker; no subagents available under Orca). Japanese
   found: the chapter-card glyphs (row above) and the font bank. Everything else is sprites, portraits, map
   tiles, UI frames and English labels.
4. 8bpp picture blocks (0x1FC000-0x200000, 0x219000-0x21E000, 0x27A000-0x280000) look like noise in 2bpp; rendered
   as snes8 (`work/sweep/p8.png`) they are backgrounds with no lettering.
5. Not covered by a static sweep: anything compressed. No decompressor has been found (`docs/re/rom.md`); the
   expander at `C0:9AB2` is a plane expansion of raw blocks, which the sweep already sees in raw form. Screens
   whose tiles `vramfind.py` cannot find raw must be re-checked when they are toured.

Whole-ROM sheets at 1x (`tools/gfx_sweep.py`, `work/sweep/s2/`) are kept for orientation only; they are
unreadable for glyphs.
