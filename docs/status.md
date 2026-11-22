# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF on dialogue, narration and card subtitles; unhooked
  renderers done; width gate open). Builds 2026-11-22 (second session): rebuild with `build.py` / `--marker`
  before testing (sha1 changes with every asm edit); card, narration, filemenu, camp warps ok on both.
- **Done:** Step 0. Phases 1-4 (`docs/re/`, `tools/debug/`, identity + roundtrip tests, `script/`). Phase 5 so far
  (details and evidence in `docs/re/vwf.md`):
  - Font decision: dialogue VWF; other paths one char per cell. English = `$0F00 + ASCII`; own 8x16 font
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
- **Next (phase 5, in this order):**
  1. Window strings: grid strings (`windows` 01CCF2: file menu items) are drawn in slices by the C8 window script
     (records near `C8:F44C`, opcodes `C1:870C` table `C1:871A`); find the slice operands so English items can be
     longer than the JP count (or note per-slice cell budgets). Check camp command list (`menus` 'term' split may
     still hold layout words: re-split `menus`/`menus_c` with the "counted" rule if the chain holds; the odd chain
     0x1BFFF-0x1C56B does, see `docs/re/text.md`).
  2. Speaker names in the marker: map each `speakers.json` name to a 6-char label in both the table and the FF15
     literal headers (they must match for portraits), then measure the name tag.
  3. Width gate for every other variant (table in `docs/re/vwf.md`; card subtitle, narration width, location label
     now measured): menus, item/class/unit lists, unit titles,
     locations, engine B boxes, battle prompts, objectives: read each budget off a marker shot (next column's x),
     record measured/guess per row. Then re-run `warp_all.py build/bounty_marker.sfc --out work/qa/marker --sheet`
     and give every sheet a visual verdict.
  4. Kanji table (translators need readable `jp`, needed before phase 6): 777 codes still `[hhhh]` (20,883 uses).
     `work/re/kanji_cand.tsv` has candidates + contexts; shape matching is weak. Read zoomed glyph sheets
     (`tools/font_sheet.py`) with script context, most used first, write `tbl/kanji.tsv`, `mktbl.py --kanji`,
     `build.py --dump --refresh`, `tools/check.py`. Codes 0x10-0x1A may be Latin Q-Z. Known: 消=2AB 去=1F1 最=275.
- **Open (not blocking):**
  - Side tables never read on a warp: battle_prompts(_b), system_prompts, descriptions, objectives (phase 8
    `textcover`). unit_records: names inside mixed records marked `data` whole.
  - VWF state at `$7F:FF80` is free by a 3-scene probe only (`tools/lua/wramfree.lua`); recheck if garbage appears.
  - Debug tool: town tavern, Mode 9 and the real ending not in the scene list; GOD/NOENC/FAST not built.
  - codex exec (used for independent visual QA) was out of quota until 2026-11-26.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session.)
