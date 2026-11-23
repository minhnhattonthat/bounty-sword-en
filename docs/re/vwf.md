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
| `C2:5641` | `$44/$46 = $EB:2D8C` in the FF0E name-tag drawer | Y >= `$A000` (English, or a pre-rendered tag cell, codes $0500-$071F: `tools/tag_font.py`) -> base `$FF:0000` | verified (phase 7: `work/qa/w_tag1704`, `w_tag1716`: "Roger", "Tsukikage" proportional, portraits matched) |
| `C0:E1CB` | same base store in the location-label drawer `C0:E1B1` (world map, chapter card) | `$2E` >= `$A000` -> `$FF` | verified (worldmap marker `L30abcdefg`, 10 cells; phase 7 "Atlas Desert" pre-rendered, `work/qa/w_tagmap`) |
| `C6:DF04` | the whole C6 printer glyph draw (chapter-card subtitle, mode 14; narration, mode 15; printer loop `C6:DD44`, code in `$20`, cursor `$7E4D7B`) | shared VWF core (`C6Vwf`, `!MODE`=1, own LAST/BASE/PX swapped in by `SwapC6`, one buffer half `$1400`); returns via `C6:DF96` | verified (card_02-06, narration markers at 160 px) |
| `C1:8E90`, `C1:8F13` | the C1 string-run loops (8E90: `$2C/2` words from `[$34]`, 19 callers incl. item lists, window op `16`; 8F13: `[count][words]` from `[$40]`, window op `02`), each word drawn by `C1:8EB9` into tile slot `$2E` (32 bytes, top tile `$7E:A000+slot*32`, bottom +`$200`; slot+1, rows of 16 slots `$20` apart) | `C1Run`: a run holding English goes through the VWF core in **mode 2** (cells = the run's slots, field cleared first, nothing spills past the last cell); word `$2020-$7E7E` = two ASCII letters (high byte first, `script_text.pack_pairs`, fixed fields of `C1_TABLES` only); `$0F7F` = TAB, PX = ceil((PX-1)/8)*8 (the first cell edge after the ink: a glyph's blank last column may spill 1 px; at an edge it stays), `$0F1F n` = SETX, PX = n*8 (grid strings; layout by `tools/grid.py`, verified 2026-11-22 on camp/status/config/items/file menus, `work/qa/warp`). All-JP runs take the original loop | partly verified 2026-11-22: battle_status lists/equipment show proportional packed markers; camp/shop lists garbled by a **marker bug**, see below |
| `C3:C71E`, `C3:C722`, `C3:C99A` | engine B per character: `JSL C1:98D5` (glyph into tile slot `C3:C823[$7E4A27]`, buffer `$7F:1800`, bottom `$1A00`, same 32-byte slot layout as `$7E:A000`) and `JSL C3:C78E` (DMA records `$7E:465B`/`$466B` = mode, src, bank, VRAM, size, chunk `$0800`; queue items `$8042`/`$8045` via `C0:967F`); C99A is the FF05 instant path (whole box uploaded by `C3:C9C3`) | `EngBGlyph`: English (and digits `$00C0-$00C9` as `0-9`) through the VWF core in **mode 3**: run = `BASEB`/`PXB`/`LASTB`, a new run when `$7E4A27` is not the cell after the last glyph (FF01, FF0E, new box, a JP glyph); `$7E4A27` still steps one cell a character, so cell layouts (FF0E, FF09 cursors) are kept. Cells from the slot table, reached as `$7E:A000 + $7800 + slot*32`. `EngBDma`: one record a half from the glyph's first slot to its spill slot (position tables C3:7447/C3:9911/C6:FEB9 are slot*16 words, so the range is linear). Name-entry field (script pointer `$7E:4D19`) keeps the original path | verified 2026-11-23: ceremony pages, guardian line (user state `rom/bounty_override.mss`), date row Yes/No cursor, name entry type/delete, shop Buy/Sell/Quit and trade-in Yes/No, item description |
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
| Speaker name tag | 6 cells, 1 char per cell (`C2:5641` path, no VWF); English is pre-rendered at build time into 48 px (`tools/tag_font.py`, names in `script/speaker_tags.tsv`, which also maps the `{spk}` headers) | marker label `K20abc` fills the tag with the portrait still matched (prologue, `work/qa/marker2/prologue/proof.png`); table name and FF15 literal must be identical. The tag copier (`C2:54A5`, slot `$1132+X` -> `$7E378D` and `[$7E3781]`) draws the matched **unit's** name, not the header: `asm/speaker_match.asm` TagSrc (hook C2:5525) swaps a unit name found as a value of `build/spk_map.bin` for its header's tag codes (packed "Old Man" drew as "l 村mn", one-letter "Thetis" as "Theti s"). FF28 off the battle map (`C2:5BDE`, `$010C & 3 = 3`) writes テティス as code immediates (C2:5BFB-5C1C): the build copies the speakers-table row into them (`rom_check.put_ff28_tag`) | measured |
| Chapter-card subtitle (master messages in card table `C6:D485`, 59) | 160 px line 1 incl. quotes (`「」` draw as `"`), centred; a second line starts at the left edge (avoid). The printer ends the message only at a line whose last word is 」 `$0037` or 』 `$0406` (`C6:DDE7`): any other last character runs on into the next message (test `test_card_subtitles_end_on_a_printer_stop`) | card_02-06 marker shots `work/qa/m_c6/` | measured |
| Narration (mode 15, master messages from table `C6:D7D8`: 7 bytes a scenario, flag ptr + two slot offsets) | 160 px a line (VWF), lines per box: JP uses up to 3 | narration marker `work/qa/m_c6/narration` (2-line message) | measured width; 3rd line guess |
| Location label (`locations`) | 10 cells, 1 char per cell; English pre-rendered into 80 px, centred to whole cells (`tools/tag_font.py`; 544 tag codes in all, ~480 used) | worldmap marker `L30abcdefg` fills the frame | measured |
| Window strings (`windows`, C1 `[count][words]` via 24-bit pointers in the C8 window scripts, drawer `C1:8F13`) | in place, count x 8 px (C1Run VWF, pairs packed). **Grid strings**: window op `02` draws the whole string into tile slots 0..n-1 (`C8:F449`: `02 0000 C1CCF2`), op `0A` DMAs `$7E:A000` to VRAM, and a tilemap shows slices of those slots (file menu `01CCF2`: ロード = slots 4-6, 消去 = 2 cells): each slice's budget = its cells x 8 px, items placed by `[0F7F]` TAB / `[0F1F][n]` SETX (`tools/grid.py`). Decoder: `tools/re/winscript.py C8F449`. Marker: label, then one 8-px code per cell (`0.`-`9.` cells 0-9, `A.`.. per `marker.CELL_CHARS`, `:` from cell 48), so each slice shows its own cells | measured per slice from `work/qa/mk_c4/<scene>/proof.png`: file menu `W6` (01CCF2) header ファイル = cells 27-30, ロード 4-6, コピー 7-9, 消去 10-11, first item 12-15 (no save) or 32-34; camp command list items 4-5 cells (1-4, 7-8, 9-10, 11-15, 16-19, 20-23, 24-28); camp orders 16-19/20-23/24-27; config `W25` (01D03A) labels 6-14, 21-24, 25-31, 32-39, values 40-43/44-47/48-53/54-59, 1-cell keys; party status labels (01C6EE) 2 cells each; ratings (01C722 at slot $2A) 1 cell each, picked by the tilemap per value | measured (screens toured). **Slice table: `docs/re/slices.tsv`** (scene, string id, first cell, cells, screen col/row), generated from tilemaps by `tools/re/slices.py` over a 20-scene menu tour (`work/qa/sl`, 119 slices); each slice's budget = cells x 8 px. Strings not in the table (windows never toured): whole string = count x 8 px. Test `test_slice_table_names_real_cells` |
| Widening a menu slice (D19) | The slices are C5 tilemap records drawn into `$7F:0800` (loop `C1:9300`, C3 script op `27 ptr24`): `40 pos16 n 02 tile16` = n cells from `tile16` at pos (row*64 + col*2), tile = VRAM base/16 + slot (`$100` for strings DMA'd to `$1000`, `$80` for `$0800`), slot = cell for cells 0-15, `$20 + cell-16` for 16-31 and so on (`C1Slot`). The frame is a C1 window def (C3 op `2D ptr24`, e.g. camp party C1:E15B): `0000 w h pos16`, then the top-right / bottom-left / bottom-right positions, then ops `04 tile16 pos16 n` (divider line, C1:968F) and `06 n tile16 pos16..` (single tiles, T junctions, C1:96A7), `08` end. C3 op `21 x y w h` follows with the same box. The C1Run field clears and draws exactly the count word's cells, so a string short of cells gets `cells` (script_text.widened: copy `[cells][words]` in the expanded ROM, window-script op 02 pointer at `refs` moved). Patches: `script/byte_patches.tsv` (05C061.., 01E15D..) | camp_party, camp, battle_menu, camp_items proofs (session ak) | measured |
| Menus, items, classes, unit names/titles, spells, constellations, orders | C1Run VWF: field cells x 8 px, up to 2 letters a word (items/classes/spells 10 cells = 80 px, unit names 6 = 48 px, titles 16 = 128 px, constellations 5 = 40 px, orders 8 = 64 px) | battle_status / camp_party_status markers (`I1The quick bro`, `C2The quick br`, `T1The quick`, `Q11Thel`) end at the window frame | items, classes, titles, constellations measured (mk_c4). **Spells**: the only code reader found is engine A `C2:6458` (`LDA $C8E0BE,x`, stride 20), which copies the record into `$7E:379F`, the dialogue variable for a spell name, so in text a spell name gets the 160 px dialogue line (measured); a menu slot is the same 10-cell C1 field as items (measured variant), so budget 80 px by rule. **Orders** (`C8:E8A6`, 16-byte records): no reader in code (no absolute/long/immediate operand for the table; the `refs` hit 182458 is graphics data); the orders the player sees are the camp-orders window strings (`windows` 01CE6C.., sliced, see `docs/re/slices.tsv`). Budget 64 px by rule (field width); phase 8 textcover |
| Engine B (ceremony, short strings) | **28 cells a row (x 16-240), 1 char per cell (the cell counter; since D18 the ink is VWF-packed, so a row's text ends left of its cells and layout gaps must be `{FF0E:n}`, not spaces), 2 rows a page**. Past cell 28 the engine wraps mid-word onto the next row, so English breaks rows with `FF01` itself; a third `FF01` row does not clear or scroll (it overwrites the two rows: write `FF03` / a new page instead) | stress build `build.py --marker --qa 1DEBD5=<ruler>`: `work/qa/w_ceremony_ruler/proof.png` (36-char ruler: row 1 ends at `c1234567` = 28th cell at the box edge, rest wrapped to row 2), `work/qa/w_ceremony_rows/proof.png` (4 `FF01` rows: only 2 show, overwritten). JP ceremony pages hold at most 2 `FF01` lines | measured |
| Engine A prompts in side tables (`system_prompts`, `battle_prompts`, `battle_prompts_b`: same opcodes as master text, `FF09`/`FF12`/`FF11`/`FF19-1E`, called by pointer from C4/C0 event scripts, e.g. `03 931341` at `C4:07EA`) | same as dialogue: 160 px a line, 3 lines a box (engine A, VWF hook `C2:4922`) | `warp.lua` `msg` scene with `--var "MSGPTR=0xC073AB"` / `0xC5E8F8`: the marker build's prompts draw in the dialogue box with the VWF and the hero name (`work/qa/w_ptr_zoom.png`). Native call sites not reached on a warp yet | measured (box = dialogue box); native context: phase 8 textcover |
| Objectives (`objectives`, `FFFE`/`FFFF`, `0401`/`0402` brackets) | unknown printer | pointed to from a 25-byte-stride data table in bank C6 (`C6:1221`, `C6:123A`.. hold `06FDD8`..). No ROM read of 0x18FD06-0x18FF48 in card_02 run on into battle (`work/qa/rr_card02`), nor on any battle-map button (`work/qa/rr_bkeys`, route `tools/routes/battle_keys.txt`) | **not measured**: reader unknown; may be unused. Real pointer table found (sixth session): `D8:FC9C`, 53 words, one per scenario, most = `FD06` (the default objective; the old `refs` 061221.. are OAM sprite data, false hits). No code reads it as an absolute operand (only byte match `BF 9C FC` at E1:CE5D is graphics data), and the full 140-scene tour `work/qa/rr_all` (`regionreads.lua`, `RANGES='18FC9C-18FF48,...'`) logged no read of the table or the text. Translate within the JP byte length; width = dialogue (160 px) as a guess |
| Descriptions (`descriptions`, 392, engine B style `FF06` fragments) | Select on a camp Gear/Pack or shop list row: position table `C3:C63C` = **2 rows of 16 cells** (box script C3:C5B0: `$7E4A29` = 32 cells, `$7E4A41` = 16 a row, `$7E4A43` = 2 rows). JP fits 16 kana a row and never breaks rows (the box wraps at cell 16; cell 32 wraps to cell 0 over row 1); `FF01` = next multiple of 16. `EngBGlyph` counts this box's cells by ink (`BASEB + ceil(PX/8) - 1`), so an English row holds 128 px, and a row before `{FF01}` <= 120 px (a full row puts the counter on cell 16 and the `FF01` lands on cell 32 = row 1). Lint: `batches.desc_problems` (pages end `FF03`, pieces `FF07`; a page opening with piece E52E/E53C/E54A has one row left) | ruler stress `work/qa/qa_desc_*` (32 letters: 2 rows, 33rd back on row 1), user state `rom/bounty_item_desc.mss` (shop) and the camp list (`work/states/en_camp_items.mss` + `work/qa/engb_desc/route.txt`): `work/qa/fix_desc_cmp.png` | measured 2026-11-23 |

Glyph torture line: all encodable ASCII + double spaces, prologue message 24FABE boxes 1-2: renders correctly.

## Marker build (`build.py --marker` -> `build/bounty_marker.sfc`, `tools/marker.py`)

All 140 warp scenes reach their scene on the marker build (`warp_all.py build/bounty_marker.sfc --out
work/qa/marker`). Master text that no longer fits its block spills per message into `$F0-$FE` (`rom_text.repack`).
Seen in the proof sheets (own read-only pass; codex was out of quota):
- dialogue boxes, shop/item/party lists, ceremony and camp lists show their markers;
- **fixed 2026-11-22 (later session)**: file menu (was in `menus` read out of word phase; now `windows.json`, shows
  markers), location label, chapter-card subtitle and narration (C6 printer, now VWF);
- **still Japanese**: (speaker name tags: English since phase 7, see the name tag row); the file menu header ファイル shows one marker letter only (slice of `01CCF2`; check the C8 script);
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
