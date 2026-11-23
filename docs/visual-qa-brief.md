# Visual-QA reviewer brief - Bounty Sword (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md` (read it with offset/limit:
  whole-file reads over ~4 KB come back as a stub under the context-mode plugin).

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Bounty Sword: speaker tags (48 px) and location labels (80 px) use short whole words by ruling D8 ("Captain",
  "Skull", "General", "D.Knight" for the JP's own Ｄ° cut); the name-entry katakana grid stays Japanese (D13, D17: input
  characters; the first page is English A-Z a-z 0-9, one letter a cell). Menu labels squeezed into 2-cell slices ("Itm", "Gdr", "Sg.", "Wp.", "Int", "Spr", "Bin", "Trd")
  are a known polish item (`docs/polish.md` "Menu grid strings"): `ok`, noted "2-cell label". Gender shows as ♂/♀.
  Card scenes (card_NN) show a scenario card: "Episode 1" on every warp is the debug select's own (progress not set).
