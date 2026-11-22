# English font, VWF and the marker build (phase 5)

## Decision (2026-11-22)

The dialogue box is 20 cells x 3 lines of 8x16 cells (verified: cell table `C2:49CE`, line-full checks `$3729` =
`$28`/`$50` at `C2:48C8`). A fixed 8-px English font would give 20 characters a line, so dialogue gets a **VWF**;
every other text path keeps one character per 8-px cell but reads an English glyph for English codes. D4 (engine work
before abbreviation) applies.

## Encoding

- English character c = word `$0F00 + ord(c)` (printable ASCII `$0F20-$0F7E`; `{}[]` are script syntax, not
  encodable). `tools/script_text.py` encodes it; JP decoding never yields ASCII. No text-kind entry uses any word
  >= `$0500`, so the range can't collide with game text.
- 「 (`$0036`) and 」 (`$0037`) stay structural: at FFFF the printer tests the word before it (`C2:48B3`): 」 FFFF
  ends a speech (FF17), anything else is a newline (FF11). The VWF draws both as `"` (4 px).

## Font (`tools/font_en.txt` -> `tools/font_en.py`)

Own design (no licence; `docs/fonts.md`). Caps 9 px (cell rows 5-13), x-height 6, descenders rows 14-15; advance =
ink width + 1, at most 8. `font_block()` lays the glyphs out like the game's font (rows of 16 glyphs, bottom tile
+$100) at **`$FF:E400`**, which is exactly where the game's own 16-bit glyph-offset formula
`((c & $FFF0) << 5) + ((c & $F) << 4)` puts codes `$0F20-$0F7F` when the base is `$FF:0000`. So any routine that
computes a JP glyph address reaches the English font by swapping only its base pointer. Advances at `$FF:0000`.

## Hooks (`asm/vwf.asm`, asar 1.91 in `tools/asar/`, applied by `build.py` after the text step)

| Org | Replaces | Does | State |
|---|---|---|---|
| `C1:86A9` | PHA / LDA #$00EB (glyph address for the C1 drawers: menus, item/class/unit lists, engine B via `C3:7554`, `C1:F876`) | English code -> `$FF` font | verified (marker tour: menus, shops, ceremony) |
| `C2:4922` | the whole engine A glyph draw (`C2:4922-49CD`, JSR from `C2:47DA`) | VWF, see below | verified (prologue torture box) |
| `C2:5641` | `$44/$46 = $EB:2D8C` in the FF0E name-tag drawer | Y >= `$E400` (English) -> base `$FF:0000` | assembled, JP path verified; English path untested (speakers still JP) |
| `C0:E1CB` | same base store in the location-label drawer `C0:E1B1` (world map, chapter card) | `$2E` >= `$E400` -> `$FF` | verified (worldmap marker `L30abcdefg`, 10 cells) |
| `C6:DF04` | the whole C6 printer glyph draw (chapter-card subtitle, mode 14; narration, mode 15; printer loop `C6:DD44`, code in `$20`, cursor `$7E4D7B`) | shared VWF core (`C6Vwf`, `!MODE`=1, own LAST/BASE/PX swapped in by `SwapC6`, one buffer half `$1400`); returns via `C6:DF96` | verified (card_02-06, narration markers at 160 px) |
| `C6:D383` | card subtitle centring (table `C6:D421`, lengths 0-19 only: 20+ read the next table and drew garbage) | centre line 1 by its pixel width (`PXSTART`) | verified (card markers centred) |

VWF (`VwfDraw`): pixel cursor `PX` from the line-run start cell `BASE`. When `$7E3729` differs from the value the
hook last wrote (`LAST`), the engine moved the cursor (newline, new box), so the run restarts there. Each glyph is
composed into its cell and, when it crosses, the next one (mask = pixels that aren't background colour 2), a cell is
cleared to background when the cursor first enters it, then `$3729` = 2 x (BASE + ceil(PX/8)) so the engine's
line-full and newline logic work unchanged, and `$3727` += 2 as before. JP glyphs go through the same path, 8 px wide.
The window buffer is re-uploaded by the game after each glyph (spill cells show: verified in the torture box).

State in `$7F:FF80-$7F:FF9D`. Free by test: `tools/lua/wramfree.lua` saw no non-zero write to `$7F:FF00-$7F:FFFF`
after boot in prologue, scen_25 (battle) and camp_items. Recheck if a scene shows garbage.

## Width gate (budgets measured in game)

| Variant | Budget | How measured | State |
|---|---|---|---|
| Dialogue line (engine A, VWF) | 160 px, 3 lines a box; more lines = `{next}` | marker lines filled to exactly 160 px end in a visible `|` at the box edge (prologue, `work/qa/m_prologue/f007340.png`); torture box | measured |
| Last dialogue line + page arrow | 160 px incl. the closing `"` | arrow sits in the border below line 3 (same shot) | measured |
| Speaker name tag | 6 cells (6 chars, fixed) | FF15 literal is 6 words | guess: measure with English speaker names |
| Chapter-card subtitle (master messages in card table `C6:D485`, 59) | 160 px line 1 incl. quotes (`「」` draw as `"`), centred; a second line starts at the left edge (avoid) | card_02-06 marker shots `work/qa/m_c6/` | measured |
| Narration (mode 15, master messages from table `C6:D7D8`: 7 bytes a scenario, flag ptr + two slot offsets) | 160 px a line (VWF), lines per box: JP uses up to 3 | narration marker `work/qa/m_c6/narration` (2-line message) | measured width; 3rd line guess |
| Location label (`locations`) | 10 cells, 1 char per cell | worldmap marker `L30abcdefg` fills the frame | measured |
| Window strings (`windows`, C1 `[count][words]` via 24-bit pointers in the C8 window scripts, drawer `C1:8F13`) | in place: each string fixed at its JP count; **grid strings are sliced** by the window script (file menu `01CCF2`: ロード = 3 cells, 最初から = 4) | filemenu marker `work/qa/m_win/filemenu` | guess: phase 7 must re-cut slices in the C8 scripts or relocate (pointers are 24-bit) |
| Menus, items, classes, unit names/titles | record width in cells (items/classes 10, unit names 6, titles 16) | C1 path, 1 char per cell | guess: measure each screen's next-column x |
| Engine B (ceremony, short strings, descriptions) | position table `$7E:4A3D`, 1 char per cell | - | guess |

Glyph torture line: all encodable ASCII + double spaces, prologue message 24FABE boxes 1-2: renders correctly.

## Marker build (`build.py --marker` -> `build/bounty_marker.sfc`, `tools/marker.py`)

All 140 warp scenes reach their scene on the marker build (`warp_all.py build/bounty_marker.sfc --out
work/qa/marker`). Master text that no longer fits its block spills per message into `$F0-$FE` (`rom_text.repack`).
Seen in the proof sheets (own read-only pass; codex was out of quota):
- dialogue boxes, shop/item/party lists, ceremony and camp lists show their markers;
- **fixed 2026-11-22 (later session)**: file menu (was in `menus` read out of word phase; now `windows.json`, shows
  markers), location label, chapter-card subtitle and narration (C6 printer, now VWF);
- **still Japanese**: speaker name tags (kept JP on purpose until names are mapped in both `speakers.json` and the
  FF15 headers); the file menu header ファイル shows one marker letter only (slice of `01CCF2`; check the C8 script);
- camp command list: marker letters mixed with `)。。`: those menu strings contain layout words decoded as characters;
  split them out of `menus` before translating.
