# Japanese left outside the extracted regions (session r sweep)

`jp_left.py build/bounty_en.sfc --orig rom/... --tbl tbl/jp.tbl --min 3` after the town-menu find (session r): 2,793
unchanged runs; minus the extracted regions and the master blocks, 1,207; the rows below are the word-like ones
(4+ kana, or kanji + 2 kana) plus the bank-C1 name lists. Most other runs are code/graphics noise. Each real string
needs its reader confirmed, a REGIONS/SPLIT entry (`tools/rom_text.py`, `tools/script_text.py`), `build.py --dump`,
English, and a warp proof. Strong leads: level-up lines 1AD465.. (上がった), battle prompts 05A530.., choice words
05EF54.. (right after the battle_prompts region end 05EF52), 0419DC (after system_prompts), 022FE2, 0EE54A (before
descriptions), 06E27A フュリス (likely the name-entry default NAME, before unit_names), name lists 0106D3..011439
(stride 0x46) and 0445A2..047467 (bank C4: unit/event data?).

## Worked (session s, 2026-11-23)

A byte-level sweep for engine A scripts (any opcode start, args by byte, ending FF00, outside the regions) found
the strings below; they and the other leads are settled as follows.

| lead | verdict |
|---|---|
| 05E954-05F001 (after battle_prompts) | **Fixed.** Engine A scripts with FF25/FF26/FF27/FF29 (3- and 6-byte arguments) flip the word phase; the old word region cut there and kept the tavern greeting, the 6 rosters, recruit/job/treasure/choice lines as `data`. `battle_prompts` is now a byte-level table (`tools/byte_scripts.py`, 27 entries). Also fixes a live bug: 05E8F8 ("Got it!", ends FF03) was relocated alone and ran on into whatever followed it in bank $F3 instead of the roster greeting. 05EBB0 (Dorn/Lena/Baron roster) has no caller: kept JP (`keep_jp.txt`). |
| 05A52E-05A582 | **Fixed**: map-command prompts (target / area / move), table `target_prompts`, callers = 3-byte pointer lists in C0:F1CE..FDA4. |
| 1AD456-1AD7C0 | **Fixed**: 8 level-up stat lines, table `level_up`, each called by `43 ptr24` just before it. |
| FF29 name buffer | **Fixed** (`asm/vwf.asm` Ff29Loop): FF29 drew each word of `$7E379F` as one glyph, so English item/spell names (packed 2 letters a word) would have printed as garbage in the chest/obtain lines. |
| 06E27A フュリス | **Fixed**: name-entry default (C6:E266 copies 12 bytes to `$7E4D1B`), `script/default_names.tsv` -> "Furis"; the name_entry warp shows `NAME Furis` (this was the old to-do 5 "フェリス"). |
| 0EE52E-0EE59E | **Fixed**: shared description sub-strings (単体に攻撃 / 複数に攻撃 / 広はんいに攻撃, FF01 FF07) called by 28 descriptions with FF06; the region started at 0EE59E, inside one call. `descriptions` now starts at 0EE52E. |
| 0419DC 移動目標を選択して下さい | **Dead**: drawn vertically by C4:193D (12 cells, `$22` += $20) inside a routine starting C4:18F1 that nothing calls (no 24-bit or 16-bit reference). Left JP. |
| 022FDC 「敵を見失いました。」 | **Fixed in place (session t)**: table `enemy_lost` (REGIONS 0x022FDC-0x022FFA, engine A, one char a word, 11 cells) -> `"Foe lost."`. No reader: no 24/16-bit reference, and never read in the 146-scene region-read tour (`work/qa/rr2`). Can't be shown with `MSGPTR` either (the sibling 041373 draws nothing there too: the FF0A 0000 box needs battle context). |
| 0106D3-011439 (C1, stride 0x46) | **Fixed (session t)**: 50 unit records C1:06D1.. (name 6 words at +2), copied whole into unit RAM by C2:21D9.. / C1:4622.. (tour: demo, scen_50, scen_51). All 48 non-hero names now English via `default_names.tsv` (names over 6 letters packed two a word, `rom_check.put_default_names`). No record name was visible on those proofs. |
| 0445A2-047467 (C4) | **Fixed (session u)**: static parser `tools/re/battle_setup.py` (format in its docstring; 231 records, 628 entries, most records abut exactly, the 1-byte gaps are a 00 after the list) finds 214 name overrides; 211 written English via `default_names.tsv` (48 px speaker-tag forms, packed two letters a word when over 6), 3 are `{FF31}` (the variable girl name, kept). 43 of them lie inside the old `unit_records` region (default names are written after the repack, so they win). Probe `tools/lua/setup_probe.lua` logs the record a scene loads (scenario 37 = record 113, its 少年 at 0475CA matches the parser) and with `COPYNAME` shows a field in the hero's status: `work/qa/w_setup2/zoom.png` "Straggler", `w_setup4/zoom.png` "Evil Spirit". Test `test_battle_setup_name_overrides_are_english`. jp_left over C4:2A39-C4:7FFF: 37 short runs left, all data noise. Notes from session t: battle-setup records (pointer table C4:2A39, 263 x 3 bytes, entry 0 = 0; parser C0:A3AE). Each unit entry has an optional name override at C0:A527: byte (unit slot), then a word; nonzero = a 6-word name copied to **`$1132 + 12*slot`**, the unit-name buffer that the battle status (C2:5525 -> `$7E378D`) and camp status (VWF FF:0423) draw. So 連邦兵 / 盗賊 / 降下猟兵 / 竜騎士団 / ダニエル / マウザー ... show JP on those units' status. A heuristic scan finds ~225 candidate fields (0x43243 盗賊 .. 0x4520B シュタイア ..); overlapping hits (e.g. 0x43ABF vs 0x43AC1) come from the slot byte forming a kanji word, so take the exact list from the parser, not the scan. The entry format has jump-table arguments (`JSR ($A69E,x)`, `($A72B,x)`), so the plan: a Lua runner that saves a state at C0:A3B0, then for each scenario index sets X = 3*i, runs to the RTL at C0:A47E and logs `[$30]+Y` at C0:A527 (and the name word); write the names via `default_names.tsv` (6 words, packed) using `unit_names`/glossary English; proof = battle_status on a scenario with an overridden enemy. `unit_records` 046CF4-0473B0 lies inside this area. |
| everything else in the table | code, graphics or data bytes that decode as kana by chance (no opcode structure, no reader). |

## Session r list

| offset | bytes | text |
|---|---|---|
| 00419A | 10 | グジバヘヰ |
| 0104B8 | 26 | 雨困ゼ前トヒだ騎超務じぼゼ |
| 0106D3 | 8 | マウザー |
| 010719 | 8 | ロジャー |
| 01075D | 10 | ・ミランダ |
| 01077E | 6 | ゜゜相 |
| 0107A5 | 10 | ファウスト |
| 0107EB | 6 | アテナ |
| 010831 | 6 | ロブン |
| 010850 | 6 | ヾヽ相 |
| 010875 | 12 | ゜シュタイア |
| 0108BD | 8 | リュウビ |
| 010901 | 10 | ヾツキカゲ |
| 010947 | 8 | ゞルーネ |
| 01098D | 14 | 仝アジャックス |
| 0109D5 | 6 | コルツ |
| 010A1B | 10 | ヘンメリー |
| 010A61 | 10 | デトニクス |
| 010AED | 6 | マイア |
| 010B0E | 6 | ・相ー |
| 010B33 | 6 | ボリス |
| 010B79 | 6 | シーナ |
| 010C05 | 6 | ズール |
| 010C4B | 6 | ドーン |
| 010CD7 | 6 | バロン |
| 010D1D | 6 | ジーン |
| 010D3C | 6 | ヾゞ相 |
| 010DA9 | 6 | ザムス |
| 010DC8 | 6 | ・・相 |
| 010DEF | 6 | リーザ |
| 010E35 | 6 | ビーン |
| 010F05 | 14 | 仝アジャックス |
| 010F4D | 8 | マクベス |
| 010F93 | 8 | ダニエル |
| 010FD9 | 6 | ノルン |
| 011065 | 8 | ロジャー |
| 0110A9 | 10 | ・ミランダ |
| 0110F1 | 6 | ロブン |
| 011137 | 8 | マウザー |
| 01117B | 12 | ゜シュタイア |
| 0111C3 | 10 | ファウスト |
| 011209 | 6 | アテナ |
| 01124F | 8 | リュウビ |
| 011293 | 10 | ヾツキカゲ |
| 0112D9 | 8 | ゞルーネ |
| 01131F | 14 | 仝アジャックス |
| 0113AD | 10 | ヘンメリー |
| 0113F3 | 6 | コルツ |
| 011439 | 10 | デトニクス |
| 01184B | 14 | ャユラレワヲヵ |
| 011BC7 | 56 | ぁいぇおきぐこざすぜたぢづとにのぱぴぷぺぽむゃゆられわを |
| 01869F | 10 | ぉぐ可家南 |
| 01D4AF | 8 | 遁首ざて |
| 022FE2 | 16 | 敵を見失いました |
| 02EAC6 | 24 | ゐヤ安た客ぜて始許十騎べ |
| 034AA0 | 16 | ヌバピヘボムヤヨ |
| 034E91 | 20 | よ起件川本伏払よれゐ |
| 0354C6 | 8 | づづすづ |
| 0419DC | 24 | 移動目標を選択して下さい |
| 0437CB | 6 | 狂ゐぃ |
| 043DB1 | 6 | 海やえ |
| 0445A2 | 8 | ダニエル |
| 04468D | 8 | マウザー |
| 044787 | 8 | ロジャー |
| 04479F | 8 | ミランダ |
| 044882 | 12 | ダークロード |
| 044B90 | 10 | ラグガドル |
| 044E40 | 12 | スカルナイト |
| 0451EF | 8 | トラップ |
| 04520B | 10 | シュタイア |
| 045640 | 12 | ダークロード |
| 0456A6 | 8 | エレボス |
| 0456C6 | 8 | ニュクス |
| 045760 | 8 | 胸むすめ |
| 045DE3 | 8 | ツキカゲ |
| 045FB5 | 6 | 嵐えぅ |
| 0461F8 | 6 | 回だげ |
| 046595 | 6 | 刃ぜげ |
| 046CC8 | 6 | 狂じぢ |
| 047467 | 8 | テティス |
| 04CCC5 | 8 | こぎ宮愛 |
| 04E88B | 8 | マウザー |
| 04E89F | 10 | ファウスト |
| 05099E | 14 | いぐぜむぴむぴ |
| 05A530 | 20 | 目標を指定して下さい |
| 05A54C | 22 | はんいを指定して下さい |
| 05A56A | 18 | どこに移動しますか |
| 05EF54 | 12 | を入手したわ |
| 05EF75 | 12 | を手に入れた |
| 05EF97 | 8 | 買わない |
| 05EFAD | 6 | 受ける |
| 05EFB7 | 8 | 受けない |
| 05EFD5 | 8 | 殺さない |
| 05EFF3 | 8 | のらない |
| 06E27A | 8 | フュリス |
| 06F4F1 | 20 | げござじず峡群荒込支 |
| 06F527 | 16 | だぢつてと未到脱 |
| 088DFF | 14 | ジ・ダ・ト・バ |
| 0924C1 | 8 | おぎおか |
| 0DA421 | 10 | 会ぇでささ |
| 0EAC5D | 12 | 憶みわわわ娘 |
| 0EB45D | 12 | 憶みわわわ娘 |
| 0EBBB7 | 6 | 毒くう |
| 0EE54A | 14 | 広はんいに攻撃 |
| 108444 | 6 | のぞ箱 |
| 10A700 | 8 | うぎぎう |
| 11A6CC | 8 | えああ東 |
| 123392 | 10 | にぉぉ同投 |
| 126994 | 10 | はく敵敵敵 |
| 12A994 | 10 | はく敵敵敵 |
| 1346A6 | 6 | 青がく |
| 135880 | 12 | 夫首讐晶のぬ |
| 14FA58 | 6 | ぐぐ調 |
| 14FB45 | 8 | げち安ぁ |
| 157B77 | 6 | ゅぁ刀 |
| 15AC84 | 12 | ぃくははたみ |
| 161364 | 8 | グググヰ |
| 16152D | 6 | 武びけ |
| 1615E3 | 16 | 面武武入入入こけ |
| 161D89 | 10 | 服入こぁチ |
| 16D626 | 6 | すご以 |
| 1762A4 | 8 | でぐ番ェ |
| 18DC96 | 10 | ゛ヽぇき追 |
| 1A0756 | 10 | 晶晶はは謎 |
| 1AD465 | 8 | 上がった |
| 1AD4E0 | 8 | 上がった |
| 1AD54E | 6 | 速さが |
| 1AD559 | 8 | 上がった |
| 1AD5D2 | 8 | 上がった |
| 1AD64E | 8 | 上がった |
| 1AD6CA | 8 | 上がった |
| 1AD74A | 8 | 上がった |
| 1AD7B2 | 8 | 上がった |
| 1AEEAD | 10 | 脱疲味ぜば |
| 1D01A8 | 6 | 祖んぢ |
