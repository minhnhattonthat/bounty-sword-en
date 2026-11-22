# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | encoding, font, both script engines, master pointer table, text inventory | encoding/font/pointer table/engine-A arg counts verified; side tables mostly guess (phase 4 confirms); kanji list open |
| [rom.md](rom.md) | header, map, free space, expansion, graphics loading | header verified; free space untested |
| [debug.md](debug.md) | main loop, game modes, leftover SCENARIO select, dialogue start, save RAM layout | verified (warp_all 140/140, save_test) |
| [vwf.md](vwf.md) | English font, encoding, VWF and menu hooks, width gate, marker build findings | dialogue VWF verified; name tag/menu budgets open |
| [graphics.md](graphics.md) | graphics-text survey | static sweep done; only the chapter card is tile-drawn Japanese |

Helpers in `tools/re/`: `words.py` (dump words / master message N), `textruns.py` (all text runs), `refs24.py`
(24-bit pointers into a range), `p24.py` (print a pointer list); `tools/gfx_map.py` + `tools/gfx_sweep_map.py`
(static graphics sweep).

Prior work: no earlier fan translation or community tools found (web search 2026-11-22; Data Crystal is on the
denied tcrf.net domain, not read).
