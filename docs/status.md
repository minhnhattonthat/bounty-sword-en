# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract (phase 3 identity build done 2026-11-22). Last build: `build/bounty_en.sfc` 2026-11-22,
  sha1 560d3eb4ec3bc40a7d5a06af2f03b19f5104f633 (= the dump), smoke ok.
- **Done:** Step 0. Phase 1 recon (`docs/re/`). Phase 2 debug tool (`tools/debug/`, `docs/re/debug.md`: warp to all
  140 scenes in `scenes.tsv` from a cold boot, `save.py` editor). Phase 3 (2026-11-22): `build.py` unpacks and
  repacks with no edits through `tools/rom_text.py`; `build.py --identity` prints "identical"; `tests/test_identity.py`
  checks identity, the master layout (2,462 slots, 2,335 messages in 9 blocks), a lossless word codec over all 65,536
  words, that an edited message moves every later pointer correctly, and that a block overflow is refused.
  - Master dialogue: messages repacked back to back per block, every slot rewritten (pointer writer proven).
  - Side tables (15 inventory regions in `REGIONS`) are only decoded and rewritten in place, same length: their
    pointers are phase 4 work.
- **Next (phase 4, skill `references/pipeline.md` §Extract):** word-by-word tokeniser on top of `rom_text.py` with
  engine A/B argument counts (`docs/re/text.md`), the FF15 speaker forms (6-word literal vs name word + FFFF), the
  `script/` files (JSON per block, ids address-based, `jp` + empty `en`), dump that never clobbers English, a
  roundtrip test over every string and a coverage test of the text ranges. Confirm each "guess" side table with a
  ROM-read log (`snes_romreads.lua`) while warping through `scenes.tsv`, find its pointers, and replace its in-place
  region with a pointer-aware table. Kanji list `tbl/kanji.tsv` (font sheets, `tools/font_sheet.py`) then
  `mktbl.py --kanji` so `jp` reads as Japanese.
- **Open (debug tool, not blocking):**
  - Town menu takes one Down then ignores further presses: the tavern (3rd entry) has no scene yet. Find the town
    menu cursor variable (`$7E00D9` changed with the first move; unconfirmed) and poke it.
  - Mode 9 (C1:B15F) not identified; the real ending sequence is not in the list yet (find it in phase 8 with
    `textcover`).
  - Save fields beyond name and map (money, units, items, levels) unmapped: needed for phase 8 stress saves.
  - Chapter cards show "Episode 1" for every scenario under the warp: the episode counter isn't set by the select.
  - GOD/NOENC/FAST globals not built.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session; MesenCE default keymap assumed.)
