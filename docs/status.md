# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (phase 1 recon done 2026-11-22). Last build: none yet.
- **Done:** Step 0 (emulator, hooks, rom.sha1, decisions D1-D7). Phase 1 (2026-11-22): encoding and 8x16 font
  verified; master dialogue table (base 0x26D5EF, 2,457 slots, 2,336 used) and engine A opcode argument counts
  (FF00-FF31; in story text only FF14 takes an argument, FF15's speaker runs to FFFF); engine B opcodes; text
  inventory of every 16-bit text run (location, class, item, unit, title tables, menu strings, battle/system
  prompts, descriptions, map objectives) in `docs/re/text.md`; free-space candidates; graphics-text survey with a
  phase-aware static sweep (only the chapter card is tile-drawn Japanese: 16x16 glyphs at 0x18449A).
  Savestates: `work/states/filemenu.mss`; intro/game states in `work/qa/orig_new/s00{1,2,3}000.mss` and
  `work/qa/orig_g1/s00{1..5}000.mss` (first town scene ~s002000, chapter card = s003000 + ~450 frames with
  `--mash 20`, first map ~s005000).
- **Next (phase 2, skill `references/emulator-qa.md` §Debug tool):**
  1. Find the scene/map variable: `$7FFD36` is the map number (indexes the location names at `C0:CB3E`); the
     master message id and engine A script pointer live at `$7E3723-3727`. Look for story flags and the chapter
     counter next to them (RAM diff between s002000 and s005000 with `ramsearch.py`).
  2. Build `tools/debug/warp.lua` + `tools/debug/scenes.tsv` (scene name -> map number / message id / flags) so a
     cold boot reaches: each chapter card (parts 1-3), each map's opening, battle, shop, status/unit menus, class
     change, save menu, game over, ending, credits. One shot per entry as proof.
  3. `save.py` for the 8 KB SRAM (3 slots): find the checksum, then edit map/units/items/names; check it loads
     without a corruption message.
  4. Later phases: side-table readers marked "guess" in `docs/re/text.md` get confirmed with a ROM-read log
     (`snes_romreads.lua`) in phase 4; kanji list `tbl/kanji.tsv` (~800 codes) in phase 4; FF15 literal speaker
     names are 6 cells and must match the name->portrait table at 0x025D5D (phase 5 design).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session; MesenCE default keymap assumed.)
