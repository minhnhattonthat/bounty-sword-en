# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- references/platform-snes.md: `snes_romreads.lua` prints `off` with the LoROM formula; on HiROM games read the file offset as `addr & 0x3FFFFF` (the probe header says so, the log column misleads).
- references/pipeline.md (§Recon): `tbl.py` is byte-greedy; with 16-bit LE codes and `FFxx` control words it decodes `FF FF 00 00` as `[FF]`+`FF00` and desyncs. Tokenise word by word in the extractor (roundtrip still holds).
- references/graphics.md (§Survey): a 512 KB-per-sheet whole-ROM render is unreadable noise; sweep at 32-64 KB per sheet.
- references/graphics.md (§Survey): graphics need not start 16-byte aligned (this game's chapter-card glyphs sit at 0x18449A); an aligned 2bpp sweep shows them as noise. Score each 4 KB block for row-to-row agreement at every even phase, keep only tile-like blocks and render each at its best phase (`tools/gfx_map.py` + `tools/gfx_sweep_map.py`): 1 MB of candidates in 34 readable sheets instead of 48 unreadable ones. Worth a skill script.
- references/pipeline.md (§Recon): text blocks can start at odd file offsets (0x280F25 here); any "is this 16-bit text" test must try both byte parities.
- references/pipeline.md (§Recon): to get a script VM's argument counts fast, list each handler's `STA <script offset>` sites with the 3-4 instructions before them (`INC A`x2, `ADC #n`), then confirm by tokenising every message and counting opcodes; handlers that rewind the pointer (`DEC A`x2) are printable name macros, not codes.
- references/emulator-qa.md (§Debug tool): before building warps by hand, look for an unreferenced debug select: grep the ROM for ASCII like `SCENARIO`/`STAGE`/`MAP` near a list of `NN:` labels. Here one RTL-continuation write (`$00EB` = C0:D8B8) opens the developers' scenario select, and its confirm path enters every scenario the game's own way (briefing, card, map).
- references/emulator-qa.md (§emu.py): emu.py with no `--frames` and no route stops at frame 0 (route_done is true at once); a warp script that queues its own presses with `L.press` needs `--frames`. And `--mash` starts at frame 0 when there is no route, so a warp must queue its own mash after the warp, or the mash drives the title menu first.
- references/emulator-qa.md (§emu.py): Mesen's Lua working folder is not always `tools/mesen` (here a relative `../debug/scenes.tsv` failed); derive the repo root from `OUT` (`OUT:match("^(.*)/work/")`) or pass absolute paths through `--var`.
- references/emulator-qa.md (§Debug tool): some menus take one cursor move and then ignore further presses at any gap (this town menu); routes that need a second Down are flaky. Poke the cursor variable instead of pressing.
- scripts/sheet.py: `is_blank` takes the tuple from `read_png`, not a path (easy to misuse from a helper).
- references/emulator-qa.md: under Claude Code's context-mode, a Read or command output over ~4 KB comes back as a stub; write tool output to a file and Read it with offset/limit (even 60-line disassemblies hit this).
- references/emulator-qa.md (§Text coverage / Hooks): a region-read probe (first read of each byte in given ranges, with PC; tools/lua/regionreads.lua here) run over the whole warp scene list confirms side-table readers in one pass; worth shipping beside textcover.lua, which logs no PC.
- references/pipeline.md (§Repo layout): Python write_text on Windows writes CRLF; pass newline="\n" when dumping script JSON or git warns and diffs churn.
- references/pipeline.md (§Recon, code = font cell): shape-matching an 8x16 hand-squeezed kanji font against MS Gothic is near useless (true kanji ranked 40-1000+); budget a context-led visual pass instead.
