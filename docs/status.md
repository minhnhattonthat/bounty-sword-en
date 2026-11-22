# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon (Step 0 setup done 2026-11-22). Last build: none yet.
- **Done:** Step 0: MesenCE qa-1 in `tools/mesen/`; original ROM boots via `tools/routes/boot.txt` and scripted Start reaches the 3-slot file menu (smoke ok); pre-commit hook (`core.hooksPath tools/hooks`) runs `tools/check.py`; guard hook in `.claude/settings.json` (stable marketplace path) blocks `sed -i`/heredoc writes, verified live; `rom.sha1` pinned; decisions D1-D7 recorded.
- **Next:** Phase 1 recon: earlier patches, text encoding (relsearch on the file menu text), pointer tables, compression, free space, graphics-text survey -> `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Keyboard input in Mesen not checked by hand: headless session; MesenCE default keymap assumed.)
