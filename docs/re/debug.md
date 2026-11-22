# Debug tool: game modes, scenario select, saves (phase 2, verified by tools/debug/warp_all.py)

## Main loop and modes (verified: RAM writes reproduce every screen below)

- The main loop runs a 24-bit continuation at `$00EB-$00ED` every frame (`JML [$EB]` style): each screen routine
  stores the next step's address there and returns with RTL. `$7E2008` non-zero = wait (fade/DMA busy).
- **Game mode** `$7E249A`; writing a mode and `$7E2496 = 1` requests the switch. Dispatcher `C0:E7F1` jumps through
  the 3-byte table at `C0:E742`:

| Mode | Init | Screen |
|---|---|---|
| 1 | C6:8C97 | boot: Pioneer logo, intro |
| 2 | C2:1ECE | attract demo battle |
| 3 | C1:402F | title file menu (最初から / ロード / コピー / 消去) |
| 6 | C1:415E | camp menu: パーティ, 作戦指示, 道具, 決意, 地図を開く, コンフィグ, ファイル |
| 7 | C2:10E4 | battle map (command menu: パーティ / 道具 / 離脱) |
| 8 | C0:C3A8 | world map |
| 9 | C1:B15F | unidentified sequence (spell effect, garbled out of context, then back to mode 1) |
| 10 | C6:CFAE | scenario briefing text |
| 11 | C1:F8D1 | TO BE CONTINUED! |
| 12 | C1:FAAF | GAME OVER |
| 13 | C1:F681 | town / event scene (sepia backdrop; town menu 武器屋 道具屋 酒場 パーティ 道具 街を出る) |
| 14 | C6:D2E6 | chapter card ("Episode 1 / <English title> / 「<Japanese title>」") |
| 15 | C6:D517 | narration text screen (same text for maps 2 and 40), then the camp |
| 16 | C6:E010 | after the prologue: picks the next scenario from `$7FFD38` (table C6:E11A) |
| 17 | C6:E679 | New Game opening ceremony (engine B) with the hero name entry |
| 18 | C2:E3AE | staff roll |
| 19 | C6:E1FC | name entry screen |

- **Scenario / map number** `$7FFD36` (word, 1-59). `C0:E00F` loads a scenario's data for it. `$7FFD38` = branch
  choice after the prologue.

## Leftover SCENARIO select (unreferenced debug code, verified)

- `C0:D8B8` (nothing points to it): draws `SCENARIO` and a label from `C0:DBAA` (8 bytes per scenario,
  `01:A-01` .. `59:A1R-`; routes A 1-10, B 11-26/30/50/51, C 31-46/54-57, extras CEX 27, DEX 28, EEX 47, FEX 48,
  GEX 49, AEX 58, A1R 59; 0, 29, 52, 53 blank). Up/down at `C0:DACE` steps `$7FFD36` 1..59; the input loop is
  `C0:D9E5`, and its confirm path `C0:D9F1` fades, calls `C0:E00F` and enters the scenario the way the game does:
  briefing (10) -> chapter card (14) -> battle map (7), or the town/event scene (13) for 1, 27, 28, 47.
- Scenario 29 and 52 load nothing. 37 goes straight to its map; 53 and 57 have no briefing.
- Cards all read "Episode 1": the episode number comes from progress the select does not set (check in phase 8).

## Dialogue start (verified)

- `C2:4561`: A = message id * 3 (masked `& 0x3FFF`); copies the 3-byte pointer from the master table `$E6:D5EF,x`
  to `$7E3723-3725`, then `JSL C2:4452`. Callers: `C0:63EB`, `C0:76F6/771D` (tables C0:7724/776C), `C0:CA80`,
  `C2:CC83` (map event triggers), `C4:0529` (event-script VM command). The warp's `msg` kind rewrites
  `$7E3723-3725` at `C2:4588` to show any message id.

## Save RAM (verified: edited save loads, tools/debug/save_test.py)

- 8 KB at `$30:6000`. Header: `+0` `84 63 4C 01`; `+4/+6/+8` 16-bit checksums of files 1-3 (sum of the slot's
  16-bit words); `+0A` used-file mask (bits 1, 2, 4 from `C1:49E8`). Files at `+000B`, `+0AAB`, `+154B` (pointer
  table `C1:4933`), 0xAA0 bytes each = a copy of WRAM `$7F:F4CB-$7F:FF6A`. Save routine `C1:4940` (writes, then
  re-sums and stores the checksum only if it matches the RAM image).
- Fields (slot offset = WRAM address - `$7FF4CB`): `+018` hero name, 6 words (padded with 0000); `+86B` scenario
  number (`$7FFD36`); `+7E5` **gold** (`$7FFCB0`, u16 LE: a 1234 poke shows "1234G" in the shop, 999999 shows
  16959 = its low word; the box reads "100G", earlier misread as 1006); `+420` the hero's item bytes (`$7FF8EB`,
  item-table index in `script/items.json` order, 0 = none; base 01 44 = Iron Sword, Buckler; status Gear shows the
  first two); `+450` the hero's Pack, 4 indexes (`$7FF91B`; base 5E x4 = Herb). Bytes at +3C0/+3D8/+3F0/+408
  (02 06 02 01) look like the same item block for other units (stride 0x18), not verified. `save.py edit --gold
  --gear --pack`; `tools/debug/stress.py` builds the stress cases from them.
- `work/saves/base.srm` (save_test.py) is written by the **original** ROM (its default ROM), so file 1 is named
  ソード; stress.py makes `base_en.srm` with the English build instead (file 1 "Sword").
- Title file menu: with any save present the cursor starts on ロード, not 最初から.
