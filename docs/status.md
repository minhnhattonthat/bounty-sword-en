# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. Release in progress (session ae). Gate = `python -X utf8 tools/release.py`. Done this session:
  jp_left 0 (C4 names), polish.md all ticked (build 647164b684bb). It will now stop at, in order: qa_gate on
  `work/qa/manifest.tsv` (build changed since the d7d9d1892cb6 tour: ~45 dialogue entries, descriptions, ceremony,
  level-up, an item name, 11 name records -> full re-tour with `warp_all.py --states --sheet` + read-only verdicts),
  story manifest (no verdicts yet), textcover (007645 / 0413E7 not yet shown). **Next, in this order:** (1)
  story pass (below); (2) re-tour + verdicts + textcover_all; (3) release.py to a zip. Story pass: chapter files exist (`tools/story_chapters.py` -> 18 files
  `work/qa/story/chapters/`, manifest `work/qa/story/manifest.tsv` initialised); codex is out of quota until
  2026-11-26 10:32, so before then read them yourself in a fresh read-only pass, one chapter at a time
  (~35 KB each: Read with offset/limit), brief = `$SKILL/assets/story-reviewer-brief.md`, write
  `work/qa/story/verdicts/<chapter id>.tsv` (`id<TAB>ok|issue<TAB>note`, id = file name without .txt), Minors to
  polish.md; re-run `story_chapters.py` + `qa_gate.py init` after text fixes and add `fixed` lines for changed
  chapters (session ae changed text in most chapters: re-run `story_chapters.py` + `qa_gate.py init` FIRST). Never
  `gh release create`.
- **Session 2026-11-23ae (phase 9, jp_left + polish):** (a) **C4 names**: a whole-ROM scan for script op 16
  (battle-setup name override: `16 slot` + 6-word name) and op 64 (`64 slot` + name; C4:E85C.. chain `62 xx
  ptr24` + `64 slot name`, and C4:E3CA) found 11 JP name records the battle_setup parser misses (043F2F 海兵隊長,
  044E40 スカルナイト "Skull", 044F91, 04695F, 04E3CC, 04E863..04E8B3): all in `script/default_names.tsv`. Not seen
  on screen (no scene known). (b) **polish.md all ticked**: ~45 dialogue fixes (repage batches `work/tl/pol*.tsv`),
  British spelling (D15), tutorial uses the real labels 'Set'/'Fight!'/'Inf', glossary forms for Immortal and the
  two mountain labels; menu-grid abbreviations and engine B letter gaps deferred as README known issues (D16).
  **Bug fixed** (seen in game): 25C52E page 5's 4th line spilled into its own box as `""Our battle is over."`.
  (c) New **`tools/show.py`** (entries by id / `--grep`: JP page view + English pages) and
  **`tools/debug/msgpages.py`** (one master message page by page: `msg` warp + KEEP + A every 90 frames, sheet in
  `work/qa/msg_<id>/`; use `sheet.py --changed 0.05 --from 1100` on it). (d) `jp_known.py --write` after the text
  changes (4 stale master tails). check 61 passed, lint 0, smoke ok, jp_left 0.
- **Session 2026-11-23ad (phase 9 start):** (a) **Live JP found by jp_left:** 「よりしろの呪符が効果を発揮した！」 at
  0x007645 (called `43 4576C0` at C0:7515) sat inside a battle_prompts_b `data` entry: side tables in `RELOCATE`
  now cut at every pointer target whose caller byte is a relocate opcode (`script_text.side_entries`) -> new text
  entry 007645 "The Yorishiro Charm took effect!". The same cut split system prompt 0413E3: C4:081E enters it one
  FF0A later (0413E7); before, that caller kept pointing at the old JP copy when the script was relocated (likely
  showed 「敵に発見されました！！」). Relocation now rewrites callers into the middle of a moved script (`inner` in
  relocs, `rom_text.repack`, allowed in `rom_check`); test `test_callers_into_a_relocated_script_follow_it`.
  Neither line seen on screen yet. (b) **`tools/jp_known.py`** classifies the build's unchanged JP runs (region /
  master / noise) and writes `docs/jp_known.txt` (1150 known; the 8 C4 names left out on purpose). (c)
  **`tools/release.py`** (build, check, smoke, jp_left --known, qa_gate on every manifest incl. story, textcover,
  polish, README placeholders, debug off, BPS + re-apply, zip patch + README.txt; refuses overwrite w/o --force).
  (d) README.md filled (status table, base ROM CRC32/MD5/SHA-1, build steps). (e) **`tools/story_chapters.py`**.
  check 61 passed, lint 0, build sha1 2000d2976f73.
- **Session 2026-11-23ac (phase 8 close):** full re-tour on d7d9d1892cb6 `work/qa/tour` 147/147 ok, 13 sheets read
  in an own read-only pass (all ok, same notes as aa: `work/qa/verdicts/tour_d7d9d1892cb6.tsv`), gate exit 0.
  `inkbox_all.py --shoot` 12/12 ok. `textcover_all.py` again ended 47 failing with "side_a: nothing to do"
  (second time; cause still unknown, the report did list the 47 engine A side lines); the same `msgcover.py
  --side` by hand: 47/47 ok, report **3545/3574 shown, 29 waived, 0 failing**. textcover_all.py now runs the
  side job a second time at the end. Smoke ok, check green.
- **Session 2026-11-23ab (phase 8, stress saves + Retreat box):** (a) **Gold found**: `$7FFCB0` u16 (save slot
  +7E5); session aa had searched for 1006 because the box was misread; it reads "100G". Also mapped: hero
  gear +420 and Pack +450 (`docs/re/debug.md`). `save.py edit --gold/--gear/--pack`. (b) New
  **`tools/debug/stress.py`** (makes `work/saves/base_en.srm` with this build's camp_save, then cases max / min /
  one, each through camp, file, items and status, plus the weapon-shop gold box held at 65535/1/0 by the new
  **`tools/lua/pokeloop.lua`**): 15/15 runs, sheets `work/qa/stress/sheets/`, verdicts
  `work/qa/verdicts_stress/` (own read-only pass: all fit). (c) **Bug fixed:** the battle-map Flee confirm
  showed **"Flee reat! Sure?"**: the box draws cells 21-23 (the 離脱 glyphs, now "Flee") then cells 2-5, so
  "Retreat!" lost its head. 01C578 spec is now `2:now! | 6:Sure? | 16:OK | 18:No | 21+3:Flee` -> "Flee now!
  Sure?" (rv14). (d) **Bug fixed:** a second name-entry default ソード at C6:EF1A (copied to $7E4D1B by C6:EEF6,
  script op 0B at 06EA39) is now "Sword" (`default_names.tsv`); no scene for it is known. (e) **inkbox_all.py**:
  `en:`/`jp:` var prefixes and a second stage `THEN_KEYS`/`THEN_FRAMES` (the warp run saves a state at its last
  frame, then the keys run from it without warp.lua). Why: on scenario warps, keys queued after SCENE_OK are
  ignored in battle menus and shops; the same keys from a savestate of that run work (`work/qa/rt7` vs `rt8`).
  Not the APU nudge (0 nudges logged; warp.lua now nudges after SCENE_OK too) and not press length (12/20
  frames fail too). Cause unknown. Row **retreat_confirm** passes match (en L8 vs jp L9). (f) `tools/lua/pclog.lua`
  (PC samples). check 60 passed, lint 0. **Promote lead:** script C3:748E (op 39 C3:6FC0, op 6C C3:BFB0, op 24 menu
  C8:EB05) is entry 10 of a C3 pointer table at file 0x1ADF3E.. (no direct reference found); camp command 4 "Go!"
  (決意) lists units with the hero greyed out (`tour/camp_resolve`) and may be the class-change list once a unit
  qualifies. Try: give the hero a promotion level with a save edit (unit records not mapped yet), then open Go!.
- **Session 2026-11-23aa (phase 8, tour + gate on f3fd66b97f7d):** full tour `work/qa/tour` **147/147 ok**
  (`--states`, so `work/states/` is from this build); 13 sheets read in a read-only pass, all ok
  (`work/qa/verdicts/tour_f3fd66b97f7d.tsv`); **`qa_gate.py check` exit 0**. `inkbox_all.py --shoot` 11/11 ok.
  `textcover_all.py` first came back 48 failing: in step 5 msgcover's side job printed "side_a: nothing to do"
  although the report listed 47 engine A side lines (re-run by hand, `msgcover.py ... --side
  work/qa/textcover/gaps_report.out --shots`: 47/47 ok; cause not found, watch for it next run), and move_prompt
  was never read: the `battle_move` route ended back on the deploy menu, so C4:193D (`LDA $C419DC,x`) never ran.
  **Scene fixed** (make_scenes.py: tail `6 b;60 -;6 up;30 -;6 a;300 -;6 x;150 -`, hold 3500; proof shows "Pick a
  destination."); its probe log is `work/qa/textcover/extra_move`. Re-report: **0 failing**. **Gold (camp/shop box "1006G") is not
  in WRAM or SRAM** as u16/u24 binary (LE or BE), packed BCD (either order), one digit per byte or word (any glyph
  base), nor as digit glyph words `C1 C0 C0 C6` (tbl C000-C900), in dumps from the camp warp (f1300), and states
  camp/shop_buy/camp_items; no `$4204-6` divider writes while the camp box draws (f400-853); the only save-window
  reads then are flags (C0:E5E4 7FFD40..4D, C1:5522.. 7FFD50..56) and unit records (C2:23DD..). Probes:
  `work/lua/{div,dig,rd,rd2}.lua` (rd2 = every WRAM read by pc, very slow). Next idea: log exec at the camp number
  box's draw (find the box call from the camp menu code) or a buy diff once the shop warp takes input.
  *Retreat* attempt: `battle_move` + KEEP + `AFTER='6 b;60 -;6 up;30 -;6 a;300 -;24 left;30 -;24 up;30 -;6 a;80 -'`
  opens Orders/Flee/Sts/Sit (`work/qa/ib_fl5/f005500.png`), but down/up in that menu did not move the cursor in two
  runs, and a third run with right/up diverged to another map view (`ib_fl7`): the real-time battle is not stable
  under different keys.
- **Session 2026-11-23z (phase 8, inkbox + a live JP box):** (a) **Bug fixed:** the battle-map box
  「移動目標を選択して下さい」 was still JP (jp_left.md had called 0419DC dead). C4:18F1 runs when X starts a move order
  after deploy (scenario 11): C4:193D sends 12 glyph words through C0:E1B1. New table **`move_prompt`** (REGIONS
  0x0419DC-0x0419F4, fixed 12, rendered as tag-font cells like the location labels: `TAG_CELLS`) -> "Pick a
  destination." (96 px field; "Choose a destination." is 106 px). New scene **`battle_move`** (make_scenes.py);
  seen `work/qa/w_move_prompt/zoom.png`. (b) inkbox row **`discard_confirm`** (camp Itm -> unit -> item -> Drop:
  windows 01CCCC "Discard it?", flush left like JP): **11/11 ok**. (c) Leads, not yet reached: *Retreat* confirm
  01C578: scenario 37 Flee leaves at once; on scenario 11 (B-01) the deploy menu is X (Set/Land/Orders/Fight!),
  after Fight! A on open ground opens Orders/Flee/Sts/Sit (`work/qa/ib_flee_en`, f5610), but the battle is real
  time and enemies walk under the cursor, so the A-press lands on a unit in some runs (`ib_flee2/3`); try a scenario
  with no nearby enemies, or poke the cursor position; the JP ROM pages the opening differently (10 vs 12 A), so a
  `match` row needs its own JP route. *Promote?* 01D38D: menu record at C8:EB05 (`02 0000 ptr C1:D38D`, then
  `02 0060 ptr C1:D2F9`), referenced as `24 00 05 EB C8` at file 0x3749C in a word-op script (not engine A/B; the
  ops around it point to C3:6FC0, C3:BFB0, C3:75C2); class-change lines (ceremony 1DF4C7.. "Dragon Knight open to X")
  say it follows a level-up. check 60 passed, lint 0, smoke ok.
- **Session 2026-11-23y (phase 8, text coverage closed):** `textcover_all.py` step 5 "gaps" swaps in whatever the
  report still lists: **sidecover jobs with `catch`** (pointer caught while it holds one table's entry, swapped to
  another table's): `engine_b` (ceremony + short_strings from the description hook C3:C52D; RAM strings the scripts
  FF06-call get an empty `{FF07}` poked first, `POKES`), `grids` (menus/windows/menus_c via `C1Run40`, `$40`),
  `engine_b_moves` (parents of FF09 operand tables, cursor moved: the first FF09 table is read only on a move;
  `ONCE=1` one swap a round); **`msgcover.py --side REPORT`** (engine A side scripts: battle/system prompts,
  level_up, target_prompts via the `$7E3723` swap, `PTRS`); **speakers** (FF15 name rows C2:5F0D.. are read by
  C2:5B3C only when a message names them; one `msg` scene per row with the probe). Waived: 22 objectives (pointer
  table D8:FC9C has no code reference; never read in two full tours), 0EF038 (no pointer/FF06 call in the original
  ROM), 2 unit_records data fragments. Seen: `work/qa/textcover/master/side_a/check.png` ("Kill him", "We've
  reach..", "Map clear", "Attack rose" typing in the dialogue box). Helper `tools/debug/unshown.py REPORT [--full]`
  groups a report by table. check 60 passed, lint 0, build unchanged (tour gate stands).
- **Session 2026-11-23x (phase 8, text coverage):** `build.py` now writes **`build/strings.tsv`** (`id<TAB>CPU
  address` of every master message and side-table text entry, from the build's own layout: `script_text.ADDR`,
  relocated engine A scripts at their copy, byte tables in bank $FE, engine B trampolines at their slot; test
  `test_strings_tsv_keys_are_where_each_string_starts`). New **`tools/debug/textcover_all.py`** (one coverage dir
  `work/qa/textcover`: master via `msgcover.py`, the 146-scene tour with `probes/textcover.lua` over the key ranges
  and `--states`, then `sidecover.py`, then `textcover.py --mask 0x3FFFFF --waive docs/text_unshown.tsv`) and
  **`tools/debug/sidecover.py` + `.lua`** (pointer swap from a scene state: each drawer call that would draw an
  entry of the table draws the next unread one while a key route redraws the menu; jobs: items, spells,
  constellations, classes, orders, unit_titles via the C1 run `$34`; descriptions via engine B `$7E4A37/39` set at
  `C3:C52D`, Select in the camp item list; readers in `docs/re/text.md`). Results: master 2335/2335, all 7 swap
  jobs complete (descriptions 193 heads, 402/405 entries read), total **3281/3573**, 4 waived with evidence
  (`docs/text_unshown.tsv`: 2 lone FF00 after FF07 sub-strings, the no-caller roster 05EBB0, enemy_lost 022FDC),
  288 failing. Open check: a swapped unit
  title is read by window op 26 but was not seen drawn on the status window (`work/qa/sc_try/unit_titles`).
  check 60 passed, lint 0, build sha1 c014fcdc11f2 (unchanged: the tour gate stands).
- **Session 2026-11-23w (phase 8, tour + gate):** full tour re-run on build c014fcdc11f2: `work/qa/tour` 146/146 ok.
  `warp_all.py --sheet` writes only `proofs_N.png`, so the gate sheets come from `sheet.py "work/qa/tour/*/proof.png"
  --div 1 --cols 4 --max 12 --out work/qa/tour/sheets/sheet.png`; then `qa_gate.py init work/qa/manifest.tsv
  work/qa/tour --glob "sheet*.png" --build build/bounty_en.sfc`. Read-only pass over all 13 sheets: all ok
  (`work/qa/verdicts/tour_c014fcdc11f2.tsv`); **`qa_gate.py check` exit 0**. Any rebuild means re-touring.
- **Session 2026-11-23v (phase 8, inkbox gate):** new **`tools/inkbox_all.py`** + **`docs/inkbox.tsv`** (one row per
  choice/centred box: warp, keys, frame, rects, mode `centre` or `match` = English ink starts where the JP ink does,
  options `side=right`, `ink=R,G,B diff=N` for text over sprites; `--shoot` warps both ROMs into
  `work/qa/ink/<row>_{en,jp}`, report `work/qa/ink/report.tsv`, exit 1 on any fail). `warp.lua` var **`AFTER`**
  (route queued at SCENE_OK, with KEEP; an emu.py `--route` replaces the scene's own keys, so use AFTER instead).
  Rows: duel/job Yes/No (engine A lists, MSG=16/17 + `tools/routes/msg_a1.txt`), ceremony date OK?, ceremony
  guardian Yes/No, shop trade-in Yes/No, file/save label boxes, status name, both shop headers: **10/10 ok**.
  **Fixes found by it:** (a) engine B Yes/No (7 shop rows 1AF6A0.., ceremony 1DECF7) put "No" one cell right of its
  cursor (the cursor tables, e.g. 1AF842 x 0x60/0x88, are JP positions; "Yes" is a cell longer than はい): gap
  `{FF0E:0003}` -> `{FF0E:0002}`, test `test_engine_b_yes_no_keeps_the_cursor_cells`. (b) Shop headers 武器屋1/道具屋1
  are centred and the digit is fixed: "Weapons 1" was 11 px off, so the labels are now "Arms"/"Item" on JP's 3 cells
  (D14; `grid_specs.tsv` 01D2B7, `byte_patches.tsv` 05B230/05B25C, rv13). Shop cursor ignores down/left/right in
  the trade-in warp (the "No" cursor was checked from the cursor table instead). check 59 passed, lint 0, smoke ok,
  build sha1 c014fcdc11f2. Worker handed back near the context limit.
- **Session 2026-11-23u (phase 8, C4 names):** static parser **`tools/re/battle_setup.py`** for the battle-setup
  records (C4:2A39, C0:A3AE/A496 format in its docstring): 214 name overrides (copied to `$1132 + 12*slot`), 211
  now English through `script/default_names.tsv` (Soldier, Dragoons, Ranger, Zodiac, M.God 1-12, Captain ...; 48 px
  speaker-tag forms), 3 `{FF31}` kept. Probe **`tools/lua/setup_probe.lua`** (record index, name writes, `COPYNAME`
  proof poke, `FIND` WRAM search; the hero is slot 4 on scenario 37). Seen: `work/qa/w_setup2/zoom.png`
  "Straggler", `w_setup4/zoom.png` "Evil Spirit" in the status. Test `test_battle_setup_name_overrides_are_english`.
- **Session 2026-11-23t (phase 8, JP-left leads):** (a) 「敵を見失いました。」 022FDC: new in-place engine A table
  **`enemy_lost`** (`rom_text.REGIONS`, `script_text` SPLIT/ENGINE_A_TABLES/RELOCATE, marker tag `A`) -> `"Foe lost."`
  (JP length = 11 one-char cells; no reader known, never read in the tour; `MSGPTR` can't show FF0A-0000 boxes, the
  verified sibling 041373 draws nothing there either). (b) Region-read tour `work/qa/rr2` (146/146, `regionreads.lua`
  over 0106D3-011439, 0445A2-047467, 022FDC-022FFA). C1 unit records (stride 0x46, name at +2) are copied into unit
  RAM by C2:21D9 / C1:4622: all 48 non-hero names English via `default_names.tsv`; `put_default_names` now packs
  two letters a word when a name is over 6 letters (Tsukikage, Hammerli, Detonics, Macbeth, Miranda). (c) **C4 lead is
  real**: battle-setup records (C4:2A39 table, parser C0:A3AE) carry optional 6-word name overrides copied by
  C0:A542 to `$1132 + 12*slot`, which the battle status (C2:5525 -> `$7E378D`) and camp status draw (watch probe,
  `work/qa/w_1132`). ~225 candidate fields (連邦兵, 盗賊, 降下猟兵, 竜騎士団, 空挺部隊, named bosses); plan in
  `docs/re/jp_left.md` (Lua runner per scenario index logging C0:A527 field addresses, then `default_names.tsv` rows).
  check 57 passed, lint 0, batches 0 problems, identity identical, smoke ok; build sha1 6b8f0dc9706d. Worker handed
  back near the context limit.
  Phase 7 closed 2026-11-23 (session k): build green and self-checking
  (`build.py` now fails on any fixed-field overflow and runs `romdiff.py` over the layout's ranges + the 8 `jml`
  hook sites, `tools/rom_check.py`); `batches.py check` 0 problems (control codes, widths, glossary); 43 tests;
  identity build still byte-identical; smoke ok. Left JP on purpose: junk/data rows (see "Skip on purpose" below),
  the kana grids of the name-entry keyboards 01C283/01C359/01C42F (input characters; keys English per D13), shop
  glyph set 01D2B7 (phase 8 to-do 1).
  Fixing a text finding: `work/tl/rvNN_fix.tsv` rows `id<TAB>page<TAB>text`, `batches.py repage rvNN FILE`,
  `check rvNN`, `merge rvNN --overwrite` (never re-merge the old `bNNN.out.tsv` files: they predate the fit pass).
  Grid strings (menus/windows/menus_c): edit `script/grid_specs.tsv`, put the ids in `work/tl/rvNN.tsv` (rows from
  `b057.tsv`), `grid.py fill rvNN script/grid_specs.tsv`, `check`, `merge --overwrite` (done that way for rv04).
- **Session 2026-11-23s (phase 8, JP-left sweep):** verdicts per lead in **`docs/re/jp_left.md` §Worked**. (a) New
  **`tools/byte_scripts.py`**: engine A tables read byte by byte (FF25/FF27/FF29/FF2A take a 3-byte address, FF26 an
  address + jump target, `docs/re/text.md`). Syntax `{FF29:7E379F}`, `{FF26:7F72B5>@1}` ... `{@1}` (label in the
  entry) or `>05E997` (an entry id); a unit (entries to an FF00 no jump leaves) stays in place if it fits, else goes
  to bank $FE (`BYTE_AREA`; `EXPANDED_TEXT` now ends at 0x3E0000) with its callers rewritten. `battle_prompts` moved
  there (05E8A2-05F001, was word region to 05EF52): tavern greeting/rosters, recruit, jobs, treasure "Obtained X!" /
  "In the chest: X!", gold, Buy/Accept/Kill/Ride choices now English. **Bug fixed on the way**: 05E8F8 "Got it!"
  ends FF03 and was relocated alone, running on into unrelated bank-$F3 bytes; now it moves with the roster greeting.
  New tables `target_prompts` (05A52E: Choose a target / an area / Where to move?) and `level_up` (1AD456..: "Attack
  rose by N!" x8). (b) **FF29 hook** `Ff29Loop` (`asm/vwf.asm`, org C2:63FB): English names in `$7E379F` are packed
  pairs; each letter now goes to the VWF (calls C2:4922 through an RTL at C2:63BB). (c) `descriptions` starts at
  0EE52E (sub-strings 単体に攻撃.. called by 28 descriptions). (d) Name-entry default フュリス -> Furis
  (`default_names.tsv` 6E27A). (e) `dump --refresh` no longer carries old `refs` (a stale false match 194AA9 would
  have been overwritten). (f) `warp.lua` `POKE` var; scene `town_tavern_roster`. **Seen in game**: `work/qa/w_roster2`
  (greeting, count, roster row Colts), `w_chest/three.png` (chest line with "Mithril Sword" poked into the buffer,
  "Attack rose by 3!", "Choose a target."), `w_name/proof.png` (NAME Furis). Test `test_byte_scripts_reach_their_english`.
  check 57 passed, lint 0, batches 0 problems, identity identical, smoke ok. Build sha1 in the commit's status.
  **Next:** open leads (022FDC 「敵を見失いました。」 reader; C1 0106D3.. and C4 0445A2.. unit-record names: read probe),
  then the full re-tour on the final build (`warp_all.py build/bounty_en.sfc --jobs 6 --out work/qa/tour --states
  --sheet`, then `find work -name _mesen -prune -exec rm -rf {} +`), `qa_gate.py init ... --build`, verdicts, gate.
- **Session 2026-11-23r (phase 8):** (a) Commits of session q (not logged here before): part cards 第1部-第3部 redrawn
  in English (`tools/card_gfx.py`, 66 tiles), status gender ♂/♀ (to-do 6 done), menu label "Pack", unit records
  never read (to-do 4 closed, keep_jp.txt), battle routes page 12 times. (b) **Full tour** on this build's
  predecessor: `work/qa/tour` 144/144 ok, states refreshed, sheets `work/qa/tour/sheets/sheet*.png` read (own fresh
  pass; verdicts `work/qa/verdicts/chunk_8365e7211a5d_000.tsv`: 4 issue, 8 ok), manifest `work/qa/manifest.tsv`
  (old one `manifest_old_p.tsv`). Issue: the battle-map command menu showed JP 離脱 = glyph words
  `[01F6][01F7][01F8]` kept in 3 grid strings (01C535, 01C578, 01CAAB) -> **"Flee"** (grid_specs `23+3:Flee` etc.;
  tutorial 290B80 now says 'Flee'); seen in game `work/qa/w_flee/zoom.png`. 01C578 ("Retreat! Sure? OK No") is not
  shown on scenario 37 (Flee leaves at once); not yet seen in game. (c) **Town command menu was all JP** (no tour
  proof showed it): 5-word records at 0x0396B2 read by `C3:966D` -> new table **`script/town_menu.json`** (Arms, Items,
  Tavern, Map, Leave, Info, Party, Pack; 40 px; glossary rows 武器屋/情報屋 allow Arms/Info), new scene `town_menu`,
  test `test_town_menu_records_are_rewritten`; seen `work/qa/w_townmenu2/z.png`. (d) **To-do 9 done: master-message
  coverage** `tools/debug/msgcover.py` (+ `msgcover.lua`, warp.lua `HOOK_STATE`): one hook state, then every slot
  swapped in and its first-byte read logged; `work/qa/cover` 2335/2335 shown, 0 waived (~10 min, 6 jobs; strings.tsv
  kept with the run). Side tables are not in its strings.tsv yet (tour + sheets cover them). (e) **JP-left sweep**
  (`jp_left.py --orig`): real JP strings remain outside the extracted regions: list + leads in
  **`docs/re/jp_left.md`** (level-up "…が上がった" 1AD465.., battle prompts 05A530.., choice words 05EF54.. after the
  battle_prompts end, 0419DC, 022FE2, 0EE54A, フュリス 06E27A = probably the name-entry default (to-do 5 reopened),
  name lists 0106D3.. and 0445A2..). **Next:** work that list (confirm each reader, add REGIONS/SPLIT, dump,
  translate, warp proof), then re-run the full tour on the final build (`warp_all.py build/bounty_en.sfc --jobs 6
  --out work/qa/tour --states --sheet`, sheets with `sheet.py ... --max 12`), `qa_gate.py init ... --build`, verdict
  the changed sheets, `qa_gate.py check`. Still open: stress saves (money/items not mapped in SRAM), inkbox on Yes/No
  and centred boxes, engine B one-char-a-cell gaps ("Qui t", polish line). check 56 passed, lint 0, identity ok.
  Worker handed back near the context limit.
- **Session 2026-11-23p (phase 8, card subtitles):** **To-do 8 done.** The C6 card printer ends a message only at a
  line whose last word is 」/』 (`C6:DDE7`); 3 cards written 『』 in JP (290540 card_02, 24DC68 card_59, 24EC3E
  table index 59, no warp scene) had become `'Title'` and ran on into the next message (card_02 showed 290558).
  Now 「Title」 (drawn `"`); 2 two-line subtitles shortened (292CC4 card_04 "The Kingdom at Sunset", 293C0A "Power
  of Darkness, Again"). Test `test_card_subtitles_end_on_a_printer_stop` (stop code + one line). All 52 card scenes
  read clean (`work/qa/cards2/sub.png`, `sub_2.png`). Probe `tools/lua/bufwrites.lua` (per-frame writes to the
  window tile halves). **Disk:** C: was full (0 B): emu.py leaves a 95 MB `_mesen` copy per run (1375 of them);
  removed, 67 GB free; after any tour run `find work -name _mesen -prune -exec rm -rf {} +` (gotcha logged).
  To-do 5 closed (warp artifact, same on the JP ROM). check 54 passed, lint 0, smoke ok. Tour states/sheets predate
  this build: re-run the full tour before the gate. **Next:** to-do 3 leftovers (buy/sell confirm lines in game,
  stress save for full bags), 4, 6, 7, 2 (polish-line abbreviations), then the chapter-card 第1部 graphics redraw,
  textcover runner (9), full tour + visual-QA verdicts into `qa_gate.py`. Worker handed back near the context limit.
- **Session 2026-11-23o (phase 8):** (a) **Tavern fixed**: `C1Run` (menu strings, VWF mode 2) shared `!PX` with
  engine A and left it at the menu's width; a dialogue box whose start `$3729` equalled `LAST` (0 after a cold warp)
  kept that PX and began at the right edge. C1Run now saves/restores PX (`asm/vwf.asm`); `work/qa/w_tav_en2` shows
  `"What'll we do? Sword"` from the left edge. (b) **To-do 1 done**: shop glyph set 01D2B7 re-laid as English cells
  (`script/grid_specs.tsv`: Weapons 0-5, Items 6-9, Smith 11-14, Clerk 17-20, Who? 22-25, Gear 26-28, Pack 29-31);
  the C5 tilemap script ops (`40 pos16 w h tile16`, w x 2 tiles; header 05B230/05B25C, nameplates 05B1C7/05B1D6,
  sell tabs 05B282/05B298) and the 3 prompt maps 01D33B (op `18`) now point at them through the new
  **`script/byte_patches.tsv`** (offset, original hex, new hex; build checks the original, romdiff logs each write;
  test `test_shop_tilemaps_point_at_the_english_cells`). 倉庫 in the sell list is a 6-word name field
  (C3:2787, C3:980F) -> "Vault" via `script/default_names.tsv`. Seen in game: `work/qa/w_shop2` (weapon/item shop),
  `work/qa/w_shop3/sell_zoom.png`. 買う/売る/やめる/何を/す were drawn but never mapped (their cells are reused).
  (c) Full tour re-run on the PX-fix build: `work/qa/tour` 144/144 ok, states refreshed (before the shop patch:
  re-run `--only` the 6 shop/tavern scenes or the whole tour before the visual-QA gate). (d) **Card lead (to-do 8)**:
  `work/qa/card02_cmp.png`: under card_02's subtitle the EN build shows lines 2-3 of the first dialogue
  (290558 "they come, Sword! / The bandits' welcoming party!") typed into the card area; the JP proof at the same
  scene shows only the subtitle. Next: shots every 10 frames on both ROMs around the card (`--shot-every 10`) to
  see whether JP draws that message later or into a hidden buffer half (`$7E374F` picks $1400/$2400; the C6
  printer uses $1400 only), then check whether VwfCommon writes engine A text into the half the card shows.
  check 53 passed, lint 0, smoke via the tour. Worker handed back at the context limit.
- **Phase 8 to do (carried from phase 7, graphics text):** (1) **done in session o** (see above). Old notes: shop menu glyph set `menus_c` 01D2B7 (買う売るやめる
  武器屋..., 2-cell words: "Buy"/"Sell" are 18 px): find how the layout words in 01D1F5 place its 32 glyph tiles on
  the shop screens, give each English word 3+ cells, then translate it with `tools/grid.py`. Seen JP on screen
  (`work/qa/shopproof/sheet.png`): header 武器屋1/道具屋1, nameplates 武器屋の主人/道具屋の娘 (の shared, 娘 1 cell),
  sell screen 誰が売る？ 倉庫 装備品 所持品. Glyph order (index 0-31): 買う売るやめる武器屋道具屋？娘　誰が何を装備品所持品と話すの主人;
  01D33B looks like 2-row tilemaps where glyph k<16 = tiles C0+k / D0+k and k>=16 = E0+(k-16) / F0+(k-16)
  (`e0 e1 c0 c1 cd / f0 f1 d0 d1 dd` = 誰が買う？). The header/nameplate tiles are not stored as byte runs (only
  chance hits at 1C7BF/1D20A): they are built by code; trace the writes to the BG tilemap (Lua on_write on VRAM or
  the WRAM tilemap buffer) on `town_weapon_shop`. (2) widen the 2-cell
  menu slices that force abbreviations (polish line "Menu grid strings"; e.g. 01D31B "Wp.Etc Gear Item Binx").
  (3) shop dialogue box: **done in session m** except the in-game read of the buy/sell lines. Measured 20 cells
  (ruler build, `work/qa/w_shopruler`); lint `batches.SHOP` (rows <= 20 cells, `{FF0E:n}` = n cells, `{FF06}`
  variables at their longest English: item 16, price 5, unit name 9; no more rows than the JP shows), test
  `test_shop_rows_fit_the_20_cell_portrait_box`; `{FF0E:n}` is now a free layout code like `{FF01}`; 24 lines
  rewritten (rv05). **Session n:** the "ignored input" was a freeze: after a scenario-select warp the sound CPU
  never echoes a command and `C2:F59F` spins at `C2:F5A2` on port $2141 (joypad polling stops; original ROM too).
  `warp.lua` now nudges it (APU_NUDGE: after 4000 polls it sets the wait counter $D9 to the port value; debug only).
  New scenes `town_tavern`, `shop_buy`, `shop_sell`, `shop_trade` all reach SCENE_OK. Read in game: a 20-cell row
  followed by `{FF01}` wraps twice, so 1AFD1A's Yes/No drew over row 1 ("TradeYes: 1NoG."); lint now requires
  <= 19 cells before `{FF01}` (test added), 11 rows fixed (rv06), trade-in confirm now right (`work/qa/w_shopx`).
  Still to read in game: buy price confirm (1AF6A0), can't-equip (1AF738), equip-now, sell confirm, bags/storage
  full (needs a full inventory: stress save). Minor: price var prints right-aligned ("Trade-in:  144G").
  **Tavern: fixed in session o (stale VWF PX).** Old note: Thetis's box shows `"What'll we` starting at the right edge
  and `e do? Sword"` cut on row 2: compare with the JP (`emu.py rom/... --script tools/debug/warp.lua --var
  "SCENE='town_tavern'"`) before fixing; it may be the tavern choice text (と話す screen).
  (4) unit_records name fields (046CF4 パラディン, 046D02 マスター/マンサー): find out if they are shown (keep_jp.txt).
  (5) **closed in session p: warp artifact.** The original ROM shows the same `NAME フェリス` under the `name_entry`
  warp (`work/qa/ne_jp/cmp.png`: JP | EN); フェリス is not in the ROM in text codes, byte/word relative search, SJIS,
  nor in WRAM as text words or keyboard-grid indices, and no script entry has it; the real New Game path (mode 17
  ceremony) defaults to "Sword" (session l). Old note: name entry shows default "NAME フェリス" (not found as text-codec bytes; another encoding or table): find it
  and add it to `script/default_names.tsv` like ソード/テティス. (6) status "Gdr 男" value still JP (polish line).
  (7) camp_items shows 倉庫 (storage tab) in JP and "Itm1": same as to-do 2. (8) **done in session p** (printer stop code). Old note: cards 02/51/53-ish: dialogue
  typed over the card subtitle area overlaps it ("to be thrown away!" eturn'"): compare with `work/qa/tour_jp`
  (same scene names) before fixing; card_31 title graphic "Anicient Weapon" (check whether the JP card has it).
  (9) textcover: no `build/strings.tsv` and no multi-message runner yet (the `msg` scene shows one message per
  boot); master addresses can come from the built pointer table (`$E6:D5EF` + 3*slot).
  Then the phase 8 done-when (skill table): warp tour sheets + read-only visual-QA verdicts (`qa_gate.py`), every
  graphics-text row English in a zoomed shot, `inkbox.py` on choice/centred boxes, stress saves, `textcover.py`.
  Tours: `work/qa/tour` (English, build of session l before the default-name/greeting fix: re-run it), `tour_jp`
  (original, same scene names). Proof sheets at full scale: `sheet.py "work/qa/tour/*/proof.png" --div 1 --cols 4
  --max 12 --out work/qa/tour/sheets/sheet.png` (sorted scene order = `ls`). Own read so far: sheets 1-8 of 12
  (scenes battle_items..scen_18); verdicts not written into a gate yet. Brief: `docs/visual-qa-brief.md`.
- **Session 2026-11-23n (phase 8, shop freeze):** see to-do 3. Also seen on the New Game path (`work/qa/w_ng3`,
  state `work/states/ng_town.mss` = first town after the ceremony): the 第1部『迫り来る恐怖』 part card is still JP
  graphics (16x16 2bpp glyphs at 0x18449A, `docs/re/graphics.md` row "Chapter card"): a phase-8 redraw item, with
  第2部/第3部. check 52 passed, lint 0, smoke ok. Worker handed back at the context limit.
- **Session 2026-11-23m (phase 8, shop box):** to-do 3 (see above). Shop states in `work/states/` refreshed on
  this build (states made on an older build show stale text tiles: cold boot or re-run `warp_all.py --states`).
  check 52 passed, lint 0 problems, smoke ok. Worker handed back at the context limit.
- **Session 2026-11-23l (phase 7 review fixes, phase 8 start):** review Important 1-4 + minors fixed:
  `tests/test_build.py` builds the English ROM (overflow/asar/romdiff gates now in `check.py`); romdiff write log
  `build/writes.txt` (pointer table, reloc callers, hooks, checksum, default names); header checksum fixed;
  `script/keep_jp.txt` (32 ids) enforced by `batches.py check`; speaker tags checked against glossary `tag "X"`
  notes (Skull, General, Ranger; objective 18FD9C "General"); `pages.wrap` balances each paragraph's last box
  (181 stub lines -> 0; stub rule in the lint); "Atlas Mountains". New: `script/default_names.tsv` (hero "Sword",
  fairy "Thetis" in the new-game records; seen in game `work/qa/w_names`); `build.py --identity` now writes
  `build/bounty_identity.sfc` (it used to overwrite the English build). 51 tests.
- **Session 2026-11-23k (phase 6 review fixes, phase 7 closed):** review Important fixed: name-entry keys (D13:
  終わり "End", 英字 "Abc", kana page keys あ/ア; seen in game: keys switch pages, typing, ← and End work,
  `work/qa/w_name3`, `w_name6`); minors fixed (PERFECT CLEAR 01C115, glossary {FF31} rule, style-reference note,
  reviews.md count) or moved to `docs/polish.md`. **D8 done** as build-time rendering: `tools/tag_font.py` draws each
  English speaker tag (48 px) and location label (80 px, centred to whole cells) into tag codes 0500-071F at
  `$FF:A000` (544 codes, ~480 used: the 16-bit glyph-offset formula wraps from 0720 on, so that is the cap);
  `script/speaker_tags.tsv` names all 107 speakers and maps the `{spk}` headers at build time (the JSON `en` keeps the
  JP header; marker/identity builds skip the rendering). Seen in game: "Roger"/"Tsukikage" tags with portraits
  (`work/qa/w_tag1704`, `w_tag1716`), "Atlas Desert" label (`w_tagmap`). `[00AB]` = 岬 (`tbl/kanji.tsv`; regenerate
  with `tools/mktbl.py --kanji tbl/kanji.tsv`: without `--kanji` it drops every kanji, and `--dump --refresh` then
  rewrites all jp).
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
  - Tag font capacity: ~480 of 544 tag codes used. A new speaker or label adds cells; if `tag_font.py` reports the
    font full, give the tags their own bank (a base other than `$FF:0000` in NameGlyph/CardGlyph).
  - Side tables still repacked in place (exact length): objectives (no reader found), unit_records; C1 tables are
    fixed fields with pair packing.
  - Side tables never read on a warp: battle_prompts(_b), system_prompts, descriptions, objectives (phase 8
    `textcover`). unit_records: names inside mixed records marked `data` whole.
  - VWF state at `$7F:FF80` is free by a 3-scene probe only (`tools/lua/wramfree.lua`); recheck if garbage appears.
  - Debug tool: town tavern, Mode 9 and the real ending not in the scene list; GOD/NOENC/FAST not built.
  - codex exec (used for independent visual QA) was out of quota until 2026-11-26.
- **Open bugs:** shop lines not all read in game yet (to-do 3); scenario warps ignore keys queued after SCENE_OK in
  shops and battle menus (debug tool; a state run takes them, session ab). (C4 battle-setup names: fixed in
  session u.)
- **Waiting on the user:** (not blocking) D15 British spelling and D16 releasing with the abbreviated menu labels
  and engine B letter gaps listed as known issues: say if either should change. (not blocking) D14 shop headers "Arms 1" / "Item 1" (3-cell labels so they stay centred);
  say if you'd rather have "Weapons"/"Items" off-centre. (Keyboard input in Mesen not checked by hand: headless session.)
