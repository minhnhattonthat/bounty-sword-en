# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- references/platform-snes.md: `snes_romreads.lua` prints `off` with the LoROM formula; on HiROM games read the file offset as `addr & 0x3FFFFF` (the probe header says so, the log column misleads).
- references/pipeline.md (§Recon): `tbl.py` is byte-greedy; with 16-bit LE codes and `FFxx` control words it decodes `FF FF 00 00` as `[FF]`+`FF00` and desyncs. Tokenise word by word in the extractor (roundtrip still holds).
- references/graphics.md (§Survey): a 512 KB-per-sheet whole-ROM render is unreadable noise; sweep at 32-64 KB per sheet.
- references/emulator-qa.md: under Claude Code's context-mode, a Read or command output over ~4 KB comes back as a stub; write tool output to a file and Read it with offset/limit (even 60-line disassemblies hit this).
