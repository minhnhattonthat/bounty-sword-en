# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (width gate: engine B, engine A prompts measured; objectives/descriptions unreached;
  left: descriptions, objectives, spells/orders lists, slice table, kanji table). Builds 2026-11-22 (fifth
  session): rebuild with `build.py` / `--marker` before testing. Full marker tour `work/qa/marker2`: 140/140, no
  garbled screen; menu re-tour `work/qa/mk_c4` 21/21.
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
- **Next (phase 5, in this order):**
  1. Width gate, remaining rows: spells and orders lists (C1 field 10 / 8 cells, guessed = field width; a warp
     to a battle spell menu or the orders list would measure them). Objectives/descriptions: no reader on any
     warp (see above); treat as measured-by-rule unless phase 8 textcover finds them.
  2. Slice table for translators: per window string, the slices the tilemaps show (start cell, cells), read off
     `work/qa/mk_c4` shots; put it in each entry's `notes` (or `docs/re/slices.tsv`) and make the fit lint use it.
  3. Kanji table (translators need readable `jp`, needed before phase 6): 777 codes still `[hhhh]` (20,883 uses).
     `work/re/kanji_cand.tsv` has candidates + contexts; shape matching is weak. Read zoomed glyph sheets
     (`tools/font_sheet.py`) with script context, most used first, write `tbl/kanji.tsv`, `mktbl.py --kanji`,
     `build.py --dump --refresh`, `tools/check.py`. Codes 0x10-0x1A may be Latin Q-Z. Known: 消=2AB 去=1F1 最=275.
- **Open (not blocking):**
  - **Side tables are repacked in place** (`rom_text.repack`: each region keeps its exact size, entries are not
    relocated and their pointers not rewritten), so today an English ceremony/prompt/description line must have the
    JP entry's byte length. Before phase 7: relocate grown entries to `$F0-$FE` and rewrite their pointers (each
    entry's `refs` lists candidates; confirm per table), or pad shorter ones; tell translators the rule in phase 6.
  - Side tables never read on a warp: battle_prompts(_b), system_prompts, descriptions, objectives (phase 8
    `textcover`). unit_records: names inside mixed records marked `data` whole.
  - VWF state at `$7F:FF80` is free by a 3-scene probe only (`tools/lua/wramfree.lua`); recheck if garbage appears.
  - Debug tool: town tavern, Mode 9 and the real ending not in the scene list; GOD/NOENC/FAST not built.
  - codex exec (used for independent visual QA) was out of quota until 2026-11-26.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session.)
