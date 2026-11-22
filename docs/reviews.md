# Batch reviews

One line per batch: who reviewed, Critical / Important found and fixed, Minors sent to `docs/polish.md`.
Orca workers can't start subagents and codex is out of quota until 2026-11-26, so reviews so far are the
translator's own fresh read-only pass (JP vs EN, glossary, voice); re-run them with codex or a reviewer agent when
one is available (the story pass in phase 9 reads every chapter again).

**Phase 6 review (2026-11-22, `.harness/reviews/bounty-sword-en-phase6.md`):** these own passes don't meet the
done-when. Fixed from it: honorifics (D11, lint now sees {hero}/{FF31} and どの), Cronus, Isolated Isle,
`{hero}'s`, Mauser's voice, `docs/style-reference.md`, brief notes. Still to do before phase 6 closes: the widow fit
pass (D12, `batches.py widows`) and an independent read-only review of every batch (table "Independent review" at the end:
codex from 2026-11-26, or a session that can dispatch `translate-retro-game:reviewer`; with neither, a fresh
worker's read-only pass of pairs it did not translate).

| Batch | Reviewer | Critical | Important | Minors |
|---|---|---|---|---|
| b001-b009 (name tables) | own pass | 0 | 0 | short forms listed in glossary |
| b010 (prologue 1) | own pass | 0 | 0 | 1 (24E4A4) |
| b011 (prologue 2) | own pass | 0 | 0 | 1 (24F91E layout) |
| b012-b013 (map hints) | own pass | 0 | 1 fixed (1E0000 called the Rheinmetall capital Romulus; Romulus is its own allied realm) | 0 |
| b014-b016 (Ruins Town, Zodiac statues, Valkyries, Salamander, Isolated Isle) | own pass | 0 | 0 | 0 |
| b017-b019 (Forgotten Island, Lake Despair, Blood Shield, ruins) | own pass | 0 | 0 | 0 |
| b020 (spell/skill shouts, combined attacks, castle entrance) | own pass | 0 | 0 | 1 (spaced-out combo shouts written in caps; check on screen in phase 8) |
| b021 (Imperial Guard, Elysion) | own pass | 0 | 1 fixed (超機神 now "Machine God Supreme" in dialogue, b013/b014 lines re-merged) | 0 |
| b022-b025 (finale, Macbeth, ending, duel/job prompts) | own pass | 0 | 0 | 1 (25C52E page flow) |
| b026-b030 (Mauser, rebel fort, Gauche, Tsukikage, Dark Wall) | own pass | 0 | 2 fixed (informer choice list lost its cursor indent: pages.py fix + rewrap; 様 kept as -sama) | 1 (278CA8 page flow) |
| b031-b032 (Crystal Cove opening, Rheinmetall capital, port) | own pass | 0 | 1 fixed (賞金かせぎ = "bounty chaser" everywhere so Thetis's "Bounty HUNTER!" correction lands; b024/b027 re-merged) | 1 (28449F placeholder) |
| b033-b043 (ship, Ophelia, Cherbourg, Koho, Daniel, Midgard, sages, Athena, desert Machine Gods No. 1-3, Corpse Immortal; game opening: East End tutorial, jobs, undead, Wolf Forest, Macbeth, Raggadol, Padova, Crimson Lake) | own pass | 0 | 1 fixed ({hero}さん written "Mister {hero}" in 2 lines, now {hero}-san like the rest) | 2 (tutorial command labels; 28CA75 open quote) |
| b044-b050 (Skull Knight duel, ruined village bandits, Dragon Knights, Faust's quiz, Highland trial and Rune, road to Ordoba, Ajax duel; 2A7D44: retreat lines, ring shouts, Romulus, Steyr, Sword Cape, volcanic island, Hydra, Gibraltar, {FF31} kidnapped) | own pass | 0 | 2 fixed (ring shouts spilled into a second box: shortened to one; 様 on Elysion kept as -sama) | 2 (placeholder speakers ××××/○○○○; shout boxes on screen) |
| b051, b052, b062 (battle prompts, system prompts) | own pass | 0 | 0 | 0 |
| b065 (ceremony), b066/b069 (short_strings, shop dialogue) | own pass | 0 | 0 | 1 (stat-up lines say "Magic"/"Spirit", the 2-cell menu labels "Int"/"Spr") |
| b067-b068 (spell/item descriptions) | own pass | 0 | 0 | 0 (no reader found; equip lines use "Eq:" and class short forms in 28-cell rows) |
| b057, b064, b058 (menus, windows, menus_c grid strings; `tools/grid.py`, specs `script/grid_specs.tsv`) | own pass + in-game shots (camp, status, config, items, file menu, battle menus: `work/qa/warp`) | 0 | 0 | 2 (2-cell labels abbreviated: Itm, Tac, Inf, Gdr, Sg., Fld, Bin, Trd, Wp.; fragment pools 01C60C/01CC4A need an on-screen check) |
| b059 (objectives, exact length, no reader) | own pass | 0 | 0 | 1 (terse: "SorcGen", "M.God 1") |

## Independent review

Pairs files from `python -X utf8 tools/pairs.py` (`>> id | JP / EN`, +-2 context), read by someone other than the
translator. One row per batch range when done.

| Batches | Reviewer | Critical | Important | Minors |
|---|---|---|---|---|
