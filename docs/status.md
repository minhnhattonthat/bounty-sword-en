# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate in progress: 2238/3539 entries in English (name tables, b010-b043: every master block up to
  master_290400's Crimson Lake, 297568); dialogue batches b044-b050 left (rest of master_290400 and 2A7D44), then
  side tables. Pace: ~10 batches per worker context; the Orca brief forbids subagents, so each worker translates itself.
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
- **Next (phase 6, translate; read `docs/translator-brief.md`, `glossary.md`, `docs/synopsis.md` first):**
  1. If `work/tl/` is gone (fresh clone): `python -X utf8 tools/batches.py split --only master_<block>` per block
     (24DB56 is done; then 1E0000 214606 257BD4 26F317 271410 280F1B 290400 2A7D44), and `--only <file>` for side
     tables. Translate each batch (`work/tl/bNNN.out.tsv`, `zip` helps for one-line-per-row tables), `check` until
     OK, `merge`, then an own read-only review line in `docs/reviews.md` (codex back 2026-11-26: use it then).
  2. Extend the synopsis and glossary as names appear (merge NEW TERMs between batches).
  3. Side tables last: ceremony/short_strings (engine B, `{FF01}` rows of 28), system/battle prompts (engine A),
     windows/menus/menus_c (C1 grid strings with `[0F7F]` cells: translate against `docs/re/slices.tsv`),
     descriptions/objectives (no reader found; translate, keep codes). Skipped rows left JP on purpose: classes
     `0BFFF2`, items `1AEDAF` (junk-looking records), orders `08E996`.. (role labels across 8-word records).
  4. First in-game look at the prologue (warp `prologue`) not done yet.
- **Open (not blocking):**
  - **Phase 7 engine work from phase 6 (D8):** speaker tag (6 cells, `C2:5641`) and location label (10 cells,
    `C0:E1B1`) must pack two letters a cell; until then `build.py` keeps the JP for the 43 overflowing entries and
    prints a warning (`script_text.OVERFLOW`). Speaker headers inside master text (`{spk}<6-word name>`) are still JP
    in `en`: map them from `speakers.json` en in phase 7 (rule-based, literal names list in the batch tool's
    terms pass). Location labels were centred with JP spaces: centre the English by pixel width.
  - `[00AB]` is 岬 (cape); add it to `tbl/kanji.tsv` and `build.py --dump --refresh` when convenient.
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
