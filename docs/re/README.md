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
| [text.md](text.md) | encoding, font, both script engines, master pointer table, text ranges | encoding/font/pointer table verified; engine-A arg counts and kanji list open |
| [rom.md](rom.md) | header, map, free space, expansion, graphics loading | header verified; free space untested |
| [graphics.md](graphics.md) | graphics-text survey | in progress (tour partial, static sweep not done) |

Prior work: no earlier fan translation or community tools found (web search 2026-11-22; Data Crystal is on the
denied tcrf.net domain, not read).
