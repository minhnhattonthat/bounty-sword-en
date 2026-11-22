# Bounty Sword English translation

Unofficial English fan translation of **Bounty Sword** (Super Famicom, Pioneer LDC, 1995): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (2,335 messages) | Translated |
| Menus, items, spells, classes, shops, battle and system messages | Translated |
| Title screen, scenario cards, graphics with text | Translated (the title logo was already English) |
| Name entry | Translated (English keyboard, default names Sword / Thetis) |
| Ending and staff roll | Translated text; the real ending has not been reached in the emulator yet |

Known issues: see [Issues](../../issues). Tested in Mesen (MesenCE) from a cold boot; start a new game on the patched
ROM rather than loading a savestate made on the Japanese one.

## Base ROM

`Bounty Sword (Japan).sfc`, 3,145,728 bytes, no copier header:

| Hash | Value |
|---|---|
| CRC32 | F3DDF35F |
| MD5 | a9ae20155ca47bcc7191b5956662a24e |
| SHA-1 | 560d3eb4ec3bc40a7d5a06af2f03b19f5104f633 |

The patched ROM is 4 MB (the text was expanded into new banks).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `asm/` | The engine patch (variable-width font, relocated text), assembled with asar 1.91. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+, your own dump of the Japanese game and asar 1.91 in `tools/asar/`
([releases](https://github.com/RPGHacker/asar/releases)).

```sh
git clone https://github.com/minhnhattonthat/bounty-sword-en
cd bounty-sword-en
# copy your dump to: rom/Bounty Sword (Japan).sfc
#   (3145728 bytes, SHA-1 560d3eb4ec3bc40a7d5a06af2f03b19f5104f633; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/bounty_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Pioneer LDC's and is included only so
the translation can be checked against it. Bounty Sword is (c) Pioneer LDC; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
