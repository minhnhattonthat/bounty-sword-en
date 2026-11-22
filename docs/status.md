# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7. Insert, fit, check: starting. Phase 6 closed 2026-11-23 (session j): 3197/3656 entries in English,
  `batches.py check` 0 problems (widows included), 0 widow boxes, independent review of every batch b001-b069 done
  (`docs/reviews.md` "Independent review": 0 Critical, 3 Important fixed in rv01-rv02, Minors in `docs/polish.md`).
  Done-when for phase 7 (skill): build green, width/overflow lint clean, control codes matched, `romdiff.py` shows
  no writes outside allowed ranges. Left JP on purpose: junk/data rows (see "Skip on purpose" below), the kana
  grids of the name-entry keyboards 01C283/01C359/01C42F (input characters; their keys are English per D13), shop
  glyph set 01D2B7 (below).
  Fixing a text finding: `work/tl/rvNN_fix.tsv` rows `id<TAB>page<TAB>text`, `batches.py repage rvNN FILE`,
  `check rvNN`, `merge rvNN --overwrite` (never re-merge the old `bNNN.out.tsv` files: they predate the fit pass).
- **Phase 7 to do (from phase 6):** (1) speaker tag / location label pair packing and speaker headers (Open, D8);
  (2) shop menu glyph set `menus_c` 01D2B7 (買う売るやめる 武器屋..., 2-cell words: "Buy"/"Sell" are 18 px): rewrite
  its layout words in 01D1F5 so each English word gets 3+ cells, then translate it with `tools/grid.py`;
  (3) widen the 2-cell menu slices that force abbreviations (polish line "Menu grid strings"); (4) `[00AB]` kanji.
- **Session 2026-11-23j (independent review b037-b069, phase 6 closed):** fresh worker, read-only pass of the
  pairs files (Read with offset/limit, ~80 lines a call): 0 Critical, 0 Important, 12 Minors to `docs/polish.md`
  (incl. US spellings Defense/armor/traveling in a British-spelled script, and 0EFCAA "Frontier Volcano Isle" vs
  the "Volcano Isle" label). Rune's Highland lines (b045/b046) carry no feminine markers in the JP, so nothing to
  restore there. `batches.py check` 0 problems, `tools/check.py` 41 passed. No text changed, so no rebuild needed.
- **Session 2026-11-23i (independent review b017-b036):** fresh worker, read-only pass: 0 Critical, 2 Important
  fixed (rv02: shout 259132 "ANOTHER DIMENSION"; old-man/old-woman register in 21618A, 217E8E, 217EF6, 215BF6),
  small fixes (273A5A, 25C374, 258F2E), Zodiac intro scenes 2721F6/28B4EB unified with the shared wording (rv03);
  10 Minors to `docs/polish.md`. Build green, smoke ok. Read pairs files with Read offset/limit (~60-75 lines a
  call): whole-file reads over ~18 KB are blocked by the context-mode hook.
- **Session 2026-11-23h (independent review b001-b016):** fresh worker, read-only pass of the pairs files: 0
  Critical, 1 Important fixed (Rune's feminine register, rv01), 4 Minors to `docs/polish.md`. Condensed reading:
  one line per entry `id | JP => EN` from `work/qa/review/bNNN.txt` (drop the context lines; read with offset/limit).
- **Session 2026-11-22g (fit pass):** widow fit pass finished and merged (see Phase). Seen in game: split box
  1E8298 (`work/qa/w_fit03`, `msg` scene, MSG=1759 = the entry's `slots` value, not its id) ends cleanly with its
  quote. Build green, smoke ok. Independent review table in `docs/reviews.md` is still empty: start at b010.
- **Session 2026-11-22f (phase 6 review fixes):** honorifics D11 (lint: `batches.HONORIFICS` + どの/さま, matches
  {hero}/{FF31}; 14 lines fixed), Cronus (glossary row クロノス; ceremony 1DEDE7), Isolated Isle (glossary row,
  275EE6), `{hero}'s` lint (295456), Mauser's オレ様 (1E6B6C, 25B114), `docs/style-reference.md` (prologue seen in
  game: `work/qa/w_prologue6`, English in the box), brief "Notes from earlier batches", minor 9 in `docs/polish.md`.
  New tools: `pages.widows`, `batches.py widows|fit|repage`, `tools/pairs.py`; tests in `tests/test_pages.py`.
  Fit pass fit01-fit02 merged (60 widow pages). Worker handed back at the context limit; resume the fit pass.
- **Session 2026-11-22e (b067, b057, b064, b058, b059 merged; phase 6 closed, reopened in f):**
  - Descriptions b067 (sign items: fragment 0EEE68 = "-born / who use it...?"; equip rows "Eq: Warrior, Knights").
  - **Grid strings** (menus/windows/menus_c): `tools/grid.py` lays English out cell by cell from
    `script/grid_specs.tsv` (`cell:text | ...`, `=` keeps JP; `fill bNNN` writes the batch); `batches.py check` runs
    `grid.problems` on them. Engine: C1Run TAB is now ceil((px-1)/8)*8 (the glyph's blank spacing column may spill
    1 px) and new `[0F1F][n]` SETX jumps to cell n (2 words), `asm/vwf.asm`; font `s` narrowed to 4 px like `c`.
    Seen in game (`work/qa/warp`: camp, party status, config, items, file menu, battle menus): aligned, no garbage.
    Test `test_grid_layout_places_each_word_in_its_cells`.
  - Objectives b059: repacked in place, so each line keeps the JP char count (check `EXACT` in `batches.py`).
- **Session 2026-11-22d (b065, b051, b069, b068 merged):**
  - Ceremony (b065) in English and seen in game (`work/qa/w_cer65`: date entry, guardian line, Yes/No fit).
    Its FF09 cursor tables (1DED1D, 1DED25, 1DF03D, 1DF045) are data: dropped from the batch, keep JP.
  - battle_prompts (b051): region now starts at 05E8A2 (the `[011E]` at 05E8A0 is the tail of the data before it)
    and is in `RELOCATE` with opcode `2E` (event-script call; 06CCA7 calls 05E8A2, 33 calls of 05EF1E).
  - **Extractor blind spot fixed:** short_strings flips word phase after the native `FF0C:F617` (one RTL byte at
    1AF617): the whole shop dialogue (buy/sell/equip/trade-in/storage-full, 1AF618..1AFDC1) was dumped as data.
    Now two REGIONS segments (1AF53F-1AF617 odd, 1AF618-1AFDC2 even; the 0x1AF349.. head is data, outside).
    `engine_b_targets(..., name)` scans every segment of a table (shop scripts call `FF06:F59F/F5A7` into the
    greeting) and cuts after each `FF10` 2-word parameter block (1AF581 `ＸＸ`, 1DECA9). `--dump --refresh` now
    only refuses a re-split that would drop an entry with English. Shop dialogue = b069, merged; greeting seen in
    `work/qa/w_shop`. Other engine B regions may hide the same phase flip after an `FF0C`: check descriptions
    (b067) for `data` entries with kana when you get there.
  - `batches.py check`: `[hhhh]` glyph words (0x60-0x4FF) are free (drop or keep), e.g. 1DEC7D `[01DE]`.
  - Descriptions: b068 done (sign items use fragment 0EEE68 "座の人が，装備して使用すると‥？": in b067 write it as
    "-born users who equip it...?" since b068 reads "For Aries{EE68}"). b067 (150 rows) left.
  - (Done in session e.) **menus_c (b058) is not a plain string table:** 01D2B7 is a 32-glyph set uploaded as tiles (layout
    words in 01D1F5) for the shop screens (武器屋 header etc.), not in `docs/re/slices.tsv`; find its slices (C1Run
    log on town_weapon_shop) before translating, and give each JP word its own cells with `[0F7F]` TABs (TAB at an
    exact cell boundary skips a whole cell: `C1Run` adds 8 after rounding down).
- **Side tables: length is no longer a blocker (session 2026-11-22c, `docs/re/text.md` §Engine B):**
  - Engine A prompts (`script_text.RELOCATE`: system_prompts, battle_prompts_b): a script (entries up to FF00; FF03
    runs on into the next entry) that grows moves whole to `$F0+` and its `03`/`43 ptr24` callers are rewritten; a
    shorter one is padded in place; a grown script with no known caller must fit (04146D "Map clear!" did).
    battle_prompts is in RELOCATE too (opcode `2E`, session d).
  - Engine B (ceremony, short_strings, descriptions, `script_text.trampolines`): an entry whose English has any other
    length gets a 10-byte FF0B jump to its copy in `$F0+`, which jumps back to the next entry. Entries under 5 words
    must keep their exact length (digits `1{FF07}`). Engine B tables now cut at FF00 (ceremony) and at every target of
    their own FF06/FF09/FF0B/FF10 pointers (incl. FF0B jump tables), so no pointer lands inside an entry (guarded).
    Verified in game (`work/qa/w_tramp2`) and by tests. system_prompts region now starts at 041373.
  - Engine B text is 1 char a cell, 28 cells a row, 2 rows a page; `{FF01}` is free in the check (add row breaks),
    a 3rd row overwrites. Engine B batches re-split: **b065 ceremony, b066 short_strings, b067-b068 descriptions**
    (old b053/b054/b055/b061 deleted). Ceremony notes: god names (1DED67..) are FF07 fragments shown inside
    " One guarded by {god}," and after "guardian spirit" on row 1: keep them <= 10 chars (Venus, Hermes, Selene,
    Apollo, Mercury, Aphrodite, Pluto, Zeus, Chronos, Uranus, Poseidon). Full-width ＭＯＮＴＨ/ＤＡＹ/ＮＡＭＥ/ＯＫ？ rows: same
    cell counts in ASCII. 1DF03D (`[0001]　[0001]ｑ奨Ｈ末Ｈ`) is data reached mid-way by FF09: drop it from the batch.
    Yes/No in 1DECF7: "Yes" is a cell longer than はい, check the cursor in phase 8.
  - Remaining side batches: see the session 2026-11-22d list above. Then a read-only review line in `docs/reviews.md`.
  - System/battle prompts are engine A scripts: `script_text.ENGINE_A_TABLES` parses their argument words
    (`{FF09:0000}`, `{FF0A:0000}`, `{FF14:0002}`). English there: ASCII `"` for 「」, keep every code.
  - Skip on purpose (junk records): b056 items `1AEDAF`, b060 orders `08E996`.., classes `0BFFF2`; b063
    unit_records are mostly data bytes around a few words (keep JP).
  - Ellipsis-only master lines (`「‥‥」`, 8 entries, e.g. 28418F) are skipped by `needs_english` and keep JP `‥‥`:
    fine on screen; check with `jp_left.py` in phase 9.
- **Session 2026-11-22 (b044-b050):** {FF12} ring shouts must fit one 3-line box (the JP does): shortened, check
  with a scan for `{next}` in `{FF12}` messages. Choice pages (before `{FF14}`): options joined by `\n`, no quotes
  (Faust's quiz 299D14..). 叫びのフエ = "Shriek Whistle" (the 80 px item name already said so). Placeholder
  speakers ××××/○○○○ -> "****" (polish line). Dark Lord = Ajax; Faust = "the Ultra-Black Sorcerer".
- **Session 2026-11-22 (b033-b043):** per batch `tl_reuse.py todo bNNN > work/tl/bNNN.todo`, write `bNNN.new.tsv`,
  `fill`, `check`, `merge`. {hero}さん = "{hero}-san", 様 = "Sir {hero}" (Roger, Ryubi lines already use it), どの =
  "{hero}-dono" (Robun). Glossary: Ophelia Les Elysion ({FF31}'s real name), Koho, Taurus, Hiomaru, Frozen Land,
  Crimson Lake, Devil's Nest, Highland, Pillars of Hercules, comrade-killer, Warlord. Tutorial (290558..) names
  Deploy / Start Battle / Retreat / MAP: match them in the battle menus (polish line).
- **Session 2026-11-22 (b022-b032):** `pages.py`: a page right before a `{FF14..}` choice code keeps the JP cursor
  indent `　` on every English line (one option a line, `\n` between; test `test_choice_list_keeps_cursor_indent...`);
  `batches.py rewrap` re-lays out merged pages after a `pages.py` change. 賞金かせぎ = "bounty chaser" (glossary).
  Tutorial lines name map/menu labels: 279ADC says "choose Rheinmetall" (location label) and 279CA6 "choose
  Information" (menus 01C4B5 情報): keep those labels matching when the side tables are translated. Yes/no RAW prompts
  (26F317, 26F34D) use two ASCII spaces where the JP has `　` before はい/いいえ: check the cursor in phase 8.
  `tools/tl_reuse.py todo|fill bNNN` reuses English for rows whose JP repeats a translated entry (Zodiac statue
  scenes recur): translate only the `todo` rows into `bNNN.new.tsv`, `fill` writes `bNNN.out.tsv`. Build green (`build.py`, smoke ok), `--identity` now repacks `jp` and
  stays byte-identical.
- **Phase 6 workflow (first session, 2026-11-22):** dialogue is authored as one paragraph per JP box
  (`tools/pages.py`, D10): `tools/batches.py` (split/check/merge/zip, adapted from the skill) shows master text as
  pages (` ‖ `), the English is pages joined by ` || `, merge wraps to 158 px x 3 lines (+`{next}` boxes) into `en`
  and keeps the paragraphs in `pages`. Brief: `docs/translator-brief.md`; glossary seeded (`glossary.md`, enforced
  by the check, which `tools/check.py` now runs); `docs/synopsis.md` (prologue); reviews in `docs/reviews.md`,
  Minors in `docs/polish.md`. Batches live in `work/tl/` (gitignored; `split` rebuilds the queue from empty `en`).
- **Done:** Step 0. Phases 1-4 (`docs/re/`, `tools/debug/`, identity + roundtrip tests, `script/`). Phase 5 so far
  (details and evidence in `docs/re/vwf.md`):
  - Font decision: dialogue VWF; C1 menus/lists VWF with packed pairs (third session); other paths one char per cell. English = `$0F00 + ASCII`; own 8x16 font
    `tools/font_en.txt` (`tools/font_en.py`), placed at `$FF:E400` in the game's font layout.
  - `asm/vwf.asm` (asar 1.91, `tools/asar/`): hooks `C1:86A9` (C1 menu/list drawers, engine B), `C2:4922` (engine A
    VWF), `C2:5641` (name tag base pointer). `build.py` pads to 4 MB and assembles; master messages that outgrow their
    block spill per message into `$F0-$FE` (`tools/rom_text.py`).
  - Marker build `build.py --marker` (`tools/marker.py`): 140/140 warp scenes reach their scene; dialogue markers fill
    exactly 160 px and show to the box edge; glyph torture box (prologue, message 24FABE) renders every glyph.
  - Fixed: speakers table split was 2 words off (records start 0x025D6D); `script/speakers.json` regenerated.
  - Tests: `tests/test_vwf.py` (font, encoding, marker structure/width), relocation test in `tests/test_identity.py`.
  - Second session: hooks `C0:E1CB` (location label), `C6:DF04` (C6 printer -> shared VWF core: card subtitle and
    narration at 160 px), `C6:D383` (card subtitle centred by pixel width). Marker: card subtitles from table
    `C6:D485`. `menus` region was read out of word phase: split into `menus`/`windows`/`menus_c`
    (`rom_text.REGIONS`, rule "counted", `head` = count word); file menu, save prompts, config and battle orders now
    extract (`script/windows.json`, 31 text entries) and show markers. Identity build still byte-identical.
  - Third session: **C1 VWF** (D4 engine work first). C1 strings are fixed in place, so `C1Run` (hooks `C1:8E90`,
    `C1:8F13`) draws English runs through the VWF core (mode 2) inside the field's own tile slots, and fixed fields
    of `script_text.C1_TABLES` pack two ASCII letters a word (`pack_pairs`): budget = cells x 8 px, up to 2 letters
    a cell. `[0F7F]` = TAB to the next cell (grid strings). Window script decoder `tools/re/winscript.py`; C1 run
    logger `tools/lua/c1runs.lua`. Test `test_c1_fields_pack_letter_pairs`. Details: `docs/re/vwf.md`.
  - Fourth session: marker bug fixed. C1 window strings split at the C8 op 02 targets (rule `anchored`, test
    `test_every_window_op02_string_has_a_text_entry`); `menus` = 7 word-phase segments (a script file may span
    several `REGIONS` rows: `script_text.region_entries`); 18 missing strings found (party-status labels...).
    `unit_titles` split into unit_titles/spells/c8_layout/constellations/c8_digits/orders (new script files).
    Window marker = label + one 8-px code per cell (`marker.window_marker`), so each tilemap slice shows its cells.
    Speaker names: `marker.speaker_labels` gives table + FF15 headers one `K<n>` label; portraits still match.
    Width gate rows updated in `docs/re/vwf.md` (name tag, window slices, C1 fields measured).
    Own visual pass of `work/qa/marker2/proofs*.png` (4 sheets): every screen shows markers or art, no garbage;
    still JP: graphics only (chapter-card 第1部 title, already in the graphics survey).
  - Fifth session: `build.py --qa ID=TEXT` (stress build of single entries -> `build/bounty_qa.sfc`; side-table
    entries must keep their exact byte length, see Open). `warp.lua` `MSGPTR` var: the `msg` scene shows any engine A
    script by CPU pointer. Width gate rows (`docs/re/vwf.md`): engine B = 28 cells x 2 rows a page, hard wrap at
    cell 28, a 3rd `FF01` row overwrites (measured, ceremony ruler); system/battle prompts are engine A scripts and
    draw in the dialogue box with the VWF (measured via MSGPTR). Probes with no hit for objectives/descriptions:
    card_02 run into battle, every battle-map button, camp item menu, item shop (`tools/routes/*_keys.txt`, emu.py `--route` beside the warp, `KEEP=true`).
  - Sixth session: objectives pointer table is `D8:FC9C` (53 words, one per scenario; the old C6 `refs` were OAM
    sprite data). Full 140-scene tour `work/qa/rr_all` with `regionreads.lua` on objectives (table + text) and
    descriptions: **no read anywhere**; rows in `docs/re/vwf.md` marked "not reached, keep JP byte length".
    Route `tools/routes/orders_keys.txt` (camp_orders + KEEP) only reaches the formation grid, not an orders list.
  - Seventh session: width rows closed (spells: engine A copies the record into the dialogue variable `$7E:379F`
    at `C2:6458`, menu slot = items' C1 field; orders: no reader, budget by rule; `docs/re/vwf.md`). **Slice
    table** `docs/re/slices.tsv` (119 slices, 20 menu scenes) generated from VRAM tilemaps + C1 run log by
    `tools/re/slices.py` (command in its docstring; rerun on the English build in phase 8); test
    `test_slice_table_names_real_cells`. **Kanji**: codes 0x200-0x38B are JIS level-1 order (愛..和, a few local
    swaps such as 大 谷 第); all 388 used codes there identified in `tbl/kanji.tsv` (`eye` = read off the sheet,
    `context` = picked from the script context among `tools/kanji_align.py` DP candidates). Unknown uses 20,883 -> 6,230.
  - Eighth session: **kanji table complete**: blocks 0x38C-0x4FF, 0x1C8-0x1F5, 0x60-0xBF read from zoomed sheets
    with script context (423 rows; `tbl/kanji.tsv` 811 rows). Proofreading the decoded script fixed four older
    picks (0x2DE 狙, 0x2E6 憎, 0x2F4 短, 0x4A3 笑). Duplicate glyphs: `canonical` in `how` makes the used code the
    canonical one (`tools/mktbl.py`, `docs/re/text.md`). Unknown uses 6,230 -> 37 (19 are later duplicate copies,
    18 truly unread: 0x25 0x7E 0xAB 0xCE 0xF0 0x1F6-0x1F8). 0x3C7 寸 (寸断のリュウビ) is low confidence.
    Identity build still byte-identical; smoke ok.
- **Phase 6 workflow (reference for retranslation; read `docs/translator-brief.md`, `glossary.md`, `docs/synopsis.md` first):**
  1. If `work/tl/` is gone (fresh clone): `python -X utf8 tools/batches.py split --only master_<block>` per block
     (24DB56 is done; then 1E0000 214606 257BD4 26F317 271410 280F1B 290400 2A7D44), and `--only <file>` for side
     tables. Translate each batch (`work/tl/bNNN.out.tsv`, `zip` helps for one-line-per-row tables), `check` until
     OK, `merge`, then an own read-only review line in `docs/reviews.md` (codex back 2026-11-26: use it then).
  2. Extend the synopsis and glossary as names appear (merge NEW TERMs between batches).
  3. Side tables last: ceremony/short_strings (engine B, `{FF01}` rows of 28), system/battle prompts (engine A),
     windows/menus/menus_c (C1 grid strings with `[0F7F]` cells: translate against `docs/re/slices.tsv`),
     descriptions/objectives (no reader found; translate, keep codes). Skipped rows left JP on purpose: classes
     `0BFFF2`, items `1AEDAF` (junk-looking records), orders `08E996`.. (role labels across 8-word records).
  4. Prologue seen in game (session f, `work/qa/w_prologue6`); voices in `docs/style-reference.md`.
- **Open (not blocking):**
  - **Phase 7 engine work from phase 6 (D8):** speaker tag (6 cells, `C2:5641`) and location label (10 cells,
    `C0:E1B1`) must pack two letters a cell; until then `build.py` keeps the JP for the 43 overflowing entries and
    prints a warning (`script_text.OVERFLOW`). Speaker headers inside master text (`{spk}<6-word name>`) are still JP
    in `en`: map them from `speakers.json` en in phase 7 (rule-based, literal names list in the batch tool's
    terms pass). Location labels were centred with JP spaces: centre the English by pixel width.
  - `[00AB]` is 岬 (cape); add it to `tbl/kanji.tsv` and `build.py --dump --refresh` when convenient.
  - Side tables still repacked in place (exact length): objectives (no reader found), unit_records; C1 tables are
    fixed fields with pair packing.
  - Side tables never read on a warp: battle_prompts(_b), system_prompts, descriptions, objectives (phase 8
    `textcover`). unit_records: names inside mixed records marked `data` whole.
  - VWF state at `$7F:FF80` is free by a 3-scene probe only (`tools/lua/wramfree.lua`); recheck if garbage appears.
  - Debug tool: town tavern, Mode 9 and the real ending not in the scene list; GOD/NOENC/FAST not built.
  - codex exec (used for independent visual QA) was out of quota until 2026-11-26.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session.)
