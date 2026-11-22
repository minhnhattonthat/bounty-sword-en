# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build (phase 4 extract done 2026-11-22). Last build: `build/bounty_en.sfc`
  2026-11-22, built from `script/` with every `en` empty, sha1 560d3eb4ec3bc40a7d5a06af2f03b19f5104f633 (= the dump),
  smoke ok.
- **Done:** Step 0. Phase 1 recon (`docs/re/`). Phase 2 debug tool (`tools/debug/`, `docs/re/debug.md`). Phase 3
  identity build (`tests/test_identity.py`). Phase 4 (2026-11-22):
  - `tools/script_text.py` + `build.py --dump [--refresh|--force]` write `script/*.json`: 9 master files (2,335
    messages, engine A tokens `{spk}` `{next}` `{hero}` `{FFxx:args}`, newline = FFFF) and 15 side-table files
    (fixed records, 0000-terminated strings, engine B scripts with argument parsing; `kind: data` for non-text,
    `refs` = 24-bit pointer candidates). Dump never overwrites a file; `--refresh` re-renders `jp` and keeps `en`.
  - `build.py` now builds from `script/` (`en` when set, else `jp`); identity still holds.
  - `tests/test_script.py`: whole-ROM roundtrip through `jp`, per-string roundtrip of every master and side entry,
    entries tile every master block and side region with no gap, every master slot reaches its entry, `script/` is
    current with the ROM, dump never clobbers English, English moves master pointers.
  - Region-read tour over all 140 scenes (`tools/lua/regionreads.lua`, `warp_all.py --script/--var`,
    `tools/re/region_reads.py`): readers confirmed for 10 of 15 side tables (`docs/re/text.md` §Readers).
- **Next (phase 5, in this order):**
  1. **Kanji table first** (translators need readable `jp`; not part of phase 4's done-when): 777 codes in text are
     still `[hhhh]` (20,883 uses). `work/re/kanji_cand.tsv` (from `tools/kanji_match.py`) has shape candidates and
     two contexts per code, but shape matching is weak here (true kanji ranked 40-1000+: hand-drawn 8x12 glyphs).
     Read zoomed glyph sheets (`tools/font_sheet.py`, `sheet.py --zoom`) in chunks with the script context, most
     used codes first, write `tbl/kanji.tsv` (code<TAB>char), then `mktbl.py --kanji tbl/kanji.tsv > tbl/jp.tbl`,
     `build.py --dump --refresh`, `tools/check.py`. Codes 0x10-0x1A may be Latin Q-Z, not kanji. Known: 消=2AB 去=1F1
     最=275 初=2A2 (from recon; 初 matched badly, re-check it).
  2. Marker build per `references/pipeline.md` §Marker: every text entry -> `[id]` marker, font/VWF decision, width
     gate. Side tables with variable-length strings still repack in place (same length); `refs` lists their
     pointer candidates for when English needs more room.
- **Open (not blocking):**
  - Side tables never read on a warp: battle_prompts, battle_prompts_b, system_prompts, descriptions, objectives
    (splits are by end codes; confirm in phase 8 with `textcover`). `system_prompts`/`battle_prompts` engine unknown,
    so their control words are not argument-parsed.
  - unit_records: names embedded in mixed records are marked `data` whole; split them out if the marker build shows
    Japanese class names left (pointer list at 0x042AE1).
  - Debug tool: town menu tavern entry has no scene; Mode 9 and the real ending not in the scene list; save fields
    beyond name and map unmapped; chapter cards always "Episode 1" under the warp; GOD/NOENC/FAST not built.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session; MesenCE default keymap assumed.)
