# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF working; marker tour done; width gate and unhooked
  renderers open). Last builds 2026-11-22: `build/bounty_en.sfc` sha1 57147fce0f44b93f09e519c5f4af30f850d1c7f5 (all
  `en` empty, 4 MB + asm), `build/bounty_marker.sfc` sha1 d211c2b9f163383a730a5580e2174a509c5bb627; both smoke ok.
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
- **Next (phase 5, in this order):**
  1. Unhooked text paths found by the marker tour (`docs/re/vwf.md` §Marker build): chapter-card location names
     (`C0:E1B1`, base-pointer hook like `C2:5641`), the `narration` scene's renderer (find it: `watch.lua` reads of
     `$EB2D8C-$EBFFFF` on scene `narration`), the file menu strings (still Japanese: not in any extracted entry; find
     the source with `tools/re/findtxt.py`/a ROM-read log on scene `filemenu`), camp command list (layout words inside
     `menus` strings: split them).
  2. Speaker names in the marker: map each `speakers.json` name to a 6-char label in both the table and the FF15
     literal headers (they must match for portraits), then measure the name tag.
  3. Width gate for every other variant (table in `docs/re/vwf.md`): menus, item/class/unit lists, unit titles,
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
