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
| `C1:8E90`, `C1:8F13` | the C1 string-run loops (8E90: `$2C/2` words from `[$34]`, 19 callers incl. item lists, window op `16`; 8F13: `[count][words]` from `[$40]`, window op `02`), each word drawn by `C1:8EB9` into tile slot `$2E` (32 bytes, top tile `$7E:A000+slot*32`, bottom +`$200`; slot+1, rows of 16 slots `$20` apart) | `C1Run`: a run holding English goes through the VWF core in **mode 2** (cells = the run's slots, field cleared first, nothing spills past the last cell); word `$2020-$7E7E` = two ASCII letters (high byte first, `script_text.pack_pairs`, fixed fields of `C1_TABLES` only); `$0F7F` = TAB to the next cell (grid strings). All-JP runs take the original loop | partly verified 2026-11-22: battle_status lists/equipment show proportional packed markers; camp/shop lists garbled by a **marker bug**, see below |
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
| Speaker name tag | 6 cells, 1 char per cell (`C2:5641` path, no VWF) | marker label `K20abc` fills the tag with the portrait still matched (prologue, `work/qa/marker2/prologue/proof.png`); table name and FF15 literal must be identical | measured |
| Chapter-card subtitle (master messages in card table `C6:D485`, 59) | 160 px line 1 incl. quotes (`「」` draw as `"`), centred; a second line starts at the left edge (avoid) | card_02-06 marker shots `work/qa/m_c6/` | measured |
| Narration (mode 15, master messages from table `C6:D7D8`: 7 bytes a scenario, flag ptr + two slot offsets) | 160 px a line (VWF), lines per box: JP uses up to 3 | narration marker `work/qa/m_c6/narration` (2-line message) | measured width; 3rd line guess |
| Location label (`locations`) | 10 cells, 1 char per cell | worldmap marker `L30abcdefg` fills the frame | measured |
| Window strings (`windows`, C1 `[count][words]` via 24-bit pointers in the C8 window scripts, drawer `C1:8F13`) | in place, count x 8 px (C1Run VWF, pairs packed). **Grid strings**: window op `02` draws the whole string into tile slots 0..n-1 (`C8:F449`: `02 0000 C1CCF2`), op `0A` DMAs `$7E:A000` to VRAM, and a tilemap shows slices of those slots (file menu `01CCF2`: ロード = slots 4-6, 消去 = 2 cells): each slice's budget = its cells x 8 px, items separated by `[0F7F]` TABs. Decoder: `tools/re/winscript.py C8F449`. Marker: label, then one 8-px code per cell (`0.`-`9.` cells 0-9, `A.`.. per `marker.CELL_CHARS`, `:` from cell 48), so each slice shows its own cells | measured per slice from `work/qa/mk_c4/<scene>/proof.png`: file menu `W6` (01CCF2) header ファイル = cells 27-30, ロード 4-6, コピー 7-9, 消去 10-11, first item 12-15 (no save) or 32-34; camp command list items 4-5 cells (1-4, 7-8, 9-10, 11-15, 16-19, 20-23, 24-28); camp orders 16-19/20-23/24-27; config `W25` (01D03A) labels 6-14, 21-24, 25-31, 32-39, values 40-43/44-47/48-53/54-59, 1-cell keys; party status labels (01C6EE) 2 cells each; ratings (01C722 at slot $2A) 1 cell each, picked by the tilemap per value | measured (screens toured); a per-string slice table for translators is still to write |
| Menus, items, classes, unit names/titles, spells, constellations, orders | C1Run VWF: field cells x 8 px, up to 2 letters a word (items/classes/spells 10 cells = 80 px, unit names 6 = 48 px, titles 16 = 128 px, constellations 5 = 40 px, orders 8 = 64 px) | battle_status / camp_party_status markers (`I1The quick bro`, `C2The quick br`, `T1The quick`, `Q11Thel`) end at the window frame | items, classes, titles, constellations measured (mk_c4); spells and orders: no warp shows them yet (guess = field width) |
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
- **fixed (fourth session)**: the marker bug below. `menus`/`windows`/`menus_c` now split by the C8 op 02 targets
  (`script_text.window_anchors`, rule `anchored`; no code or other window op points into `C1:BFFF-D3AB`), and
  `menus` is seven word-phase segments (11/13-byte layout records flip the phase; 18 strings at even offsets were
  missing, among them the party-status labels `01C6EE`). `unit_titles` was five tables: now `unit_titles`
  (16 words from `C8:DF5E`), `spells`, `c8_layout`, `constellations`, `c8_digits`, `orders`. Full tour
  `work/qa/marker2`: 140/140, largest C1 run = a real string (n=106), no garbage screens. Speaker names now
  show as `K<n>` labels with portraits.
- **marker bug (2026-11-22, C1Run tour `work/qa/mk_c1`)**: `menus`/`menus_c` use the `term` split, so the marker
  overwrites the count words of `[count][words]` strings there. `tools/lua/c1runs.lua` on town_item_shop logged
  `run40 n=3951 ptr=C1D2F9` (count word replaced by `o` = `$0F6F`): the run clears ~4000 slots and the camp and
  shop screens fill with garbage. The original-path build drew the same bad count more quietly. Fix: split both
  regions by the window-script op `02` pointers (`02 pos16 ptr24` into `C1:BFFF-C1:D3AB`; the counted chain holds
  only in stretches: `C1:D2F9` 16, `C1:D31B` 15, then breaks; `C1:BFFF` 12 strings to `C1:C283`).
