# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- references/platform-snes.md: `snes_romreads.lua` prints `off` with the LoROM formula; on HiROM games read the file offset as `addr & 0x3FFFFF` (the probe header says so, the log column misleads).
- references/pipeline.md (§Recon): `tbl.py` is byte-greedy; with 16-bit LE codes and `FFxx` control words it decodes `FF FF 00 00` as `[FF]`+`FF00` and desyncs. Tokenise word by word in the extractor (roundtrip still holds).
- references/graphics.md (§Survey): a 512 KB-per-sheet whole-ROM render is unreadable noise; sweep at 32-64 KB per sheet.
- references/graphics.md (§Survey): graphics need not start 16-byte aligned (this game's chapter-card glyphs sit at 0x18449A); an aligned 2bpp sweep shows them as noise. Score each 4 KB block for row-to-row agreement at every even phase, keep only tile-like blocks and render each at its best phase (`tools/gfx_map.py` + `tools/gfx_sweep_map.py`): 1 MB of candidates in 34 readable sheets instead of 48 unreadable ones. Worth a skill script.
- references/pipeline.md (§Recon): text blocks can start at odd file offsets (0x280F25 here); any "is this 16-bit text" test must try both byte parities.
- references/pipeline.md (§Recon): to get a script VM's argument counts fast, list each handler's `STA <script offset>` sites with the 3-4 instructions before them (`INC A`x2, `ADC #n`), then confirm by tokenising every message and counting opcodes; handlers that rewind the pointer (`DEC A`x2) are printable name macros, not codes.
- references/emulator-qa.md: under Claude Code's context-mode, a Read or command output over ~4 KB comes back as a stub; write tool output to a file and Read it with offset/limit (even 60-line disassemblies hit this).
