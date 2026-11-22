# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 done 2026-11-22). Last build: none yet.
- **Done:** Step 0 (emulator, hooks, rom.sha1, decisions D1-D7). Phase 1 so far (2026-11-22): no earlier patch found;
  encoding verified (16-bit LE codes, kana/latin/symbol rows; `tbl/jp.tbl` from `tools/mktbl.py`, roundtrip ok);
  8x16 font at $EB:2D8C traced (`tools/font_sheet.py`); master dialogue pointer table (2,333 x 24-bit at 0x26D772)
  covering ~300 KB of text; intro VM (engine B) opcodes and arg counts; dialogue VM (engine A) dispatch table;
  header, free-space candidates, graphics loader (no LZ seen). Notes: `docs/re/{text,rom,graphics}.md`.
  Savestates: `work/states/filemenu.mss`; intro/game states in `work/qa/orig_new/s00{1,2,3}000.mss` and
  `work/qa/orig_g1/s00{1..5}000.mss` (first town scene ~s002000, first map ~s005000).
- **Next (to finish phase 1):**
  1. Engine A argument counts: read each handler at the `$C2:4A67` table for word reads (`LDA [$48],y` + `INY INY`);
     confirm FF15 speaker form (name or FF1F/FF28 id). Then decode a few hundred messages from the master table with a
     word-tokeniser and check no desync.
  2. Map the menu/item/unit/spell string tables (C1 menu strings at 0x1C285+, the other kana regions listed in
     `docs/re/text.md`): who reads them, pointer form.
  3. Graphics survey: check the name-entry grid and chapter card (font or tiles: dump VRAM, `vramfind.py`), then a
     static sweep with `tools/gfx_sweep.py` at 32-64 KB per sheet over graphics banks; fill `docs/re/graphics.md`.
  4. Kanji list (`tbl/kanji.tsv`, code<TAB>char) can start here or in phase 4: ~800 codes, read off font sheets with
     script context.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session; MesenCE default keymap assumed.)
