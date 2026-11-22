# Translator brief - Bounty Sword

Read with offset/limit (files over ~4 KB come back as a stub otherwise): `glossary.md` (rulings, style, terms),
`docs/style-reference.md` (voices, approved and corrected examples), `docs/synopsis.md`, your batch
`work/tl/bNNN.tsv` and its terms `build/terms_bNNN.txt`.

## Input
`work/tl/bNNN.tsv`: `id<TAB>speaker<TAB>form<TAB>limit<TAB>JP`.
- `dlg` (master dialogue): JP pages (one JP box each) joined by ` ‖ `, lines by ` / `, `<name>` = who speaks from
  that page on (`<HERO>` = the hero {FF1F}, `<FF28>` = the fairy, `<FF31>` = the variable second name).
  `{FF2F}`/`{FF30}` before a page = a conditional one-line list item (a ring name); `{FF12}` = spell shout prefix.
  `RAW` = a yes/no prompt: write the whole message in script syntax with every `{...}` code kept, `\n` = FFFF.
- side tables (`items`, `ceremony`...): script syntax; keep every `{FFxx...}` and `[hhhh]` code; `{FF01}` (engine B
  row break, 28 characters a row) may be placed freely.

## Output
`work/tl/bNNN.out.tsv`, written with the file-write tool: `id<TAB>English`, every id once, same order, plain ASCII.
- `dlg`: one paragraph per JP page, pages joined by ` || ` (same count as the ` ‖ ` pages). Keep `"` at the start/end
  of a page where the JP page has 「/」. Keep {hero} {FF31} {FF1F} {FF28} {FF2B} inline. Do not wrap: the tool wraps
  to 158 px x 3 lines and adds boxes. `\n` forces a line break; `{next}` forces a new box (avoid on {FF2F} lines).
- Check: `python -X utf8 tools/batches.py check bNNN` until it prints OK. Merge: `tools/batches.py merge bNNN`.

## Quality bar (mistakes made before, in this and other projects)
- Names exactly as `glossary.md` (Steyr, not Steyer). A JP term in the line needs its EN form (the check enforces it).
- Voice: keep each speaker's register (glossary Style rules); the fairy's teasing and the old men's rambling are not
  neutral English. A flattened quirk or dead joke counts as Important in review.
- No suffix glued to a variable ({FF2B}th); no "a/an" right before {hero}/{FF31}; no "'s" after them.
- One JP page = one English page; don't move content between pages (the order of boxes is the game's pacing).
- Don't over-explain; don't add content. ‥‥ pauses -> "..." (keep the pause beats).

## Notes from earlier batches (reviewer lessons; add each new one here)
- Box fit: a page is one box of 3 lines (~70-80 chars). Don't let the wrap push the last 1-3 words into a box of
  their own (`batches.py check` flags a "widow box"); tighten the line or end the box at a sentence boundary.
  Dry-run: `python -X utf8 tools/batches.py fit '"page text"'`.
- Honorifics stay on names and on {hero}/{FF31}: {hero}さん = "{hero}-san", 様 = "-sama" ({hero}-sama,
  {FF31}-sama), どの = "-dono"; never "Sir {hero}" / "Lady {FF31}" (D1, glossary Rulings).
- Mauser's オレ様 is a brag: "the great Mauser", not a plain "I". Miranda: no contractions.
- {FF12} ring and spell shouts must fit one 3-line box (the JP does).
- A page right before a `{FF14}` choice code: one option a line, joined by `\n`, no quotes (the tool keeps the
  cursor indent).
- 賞金かせぎ = "bounty chaser" ({FF31}'s slight; Thetis corrects it to "Bounty HUNTER!").
- One god, one spelling: Cronus (not Chronos/Kronos). Place names as in the glossary (Isolated Isle, not a
  description of it).
- Placeholder speakers ××××/○○○○ -> "****".

## Report (final message)
`NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was dropped`.
