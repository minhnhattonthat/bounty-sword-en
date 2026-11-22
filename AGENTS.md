# Bounty Sword (SNES) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/bounty_en.sfc (checks the dump against `rom.sha1` first; written in phase 3)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/bounty_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/bounty_en.sfc --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.tsv`, phase 2; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user; phase 9)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Bounty Sword (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). HiROM (header at $FFC0, map $31), 3 MB, Pioneer LDC 1995.
- Emulator: this repo's own MesenCE QA fork in `tools/mesen/` (release `qa-1`, https://github.com/minhnhattonthat/MesenCE/releases/download/qa-1/Mesen_qa-1_Windows.zip; gitignored; `python -X utf8 $SKILL/scripts/fetch_emu.py mesen` restores it). Savestates: `work/states/`.
- Text: `script/` (TSV). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`. Codecs copied from the skill: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Boot route: Start at f1500 skips the intro; title "PUSH START BUTTON" by ~f2200; Start there opens the 3-slot file menu.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
