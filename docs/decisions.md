# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-22 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-22 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-22 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-22 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default). |
| D5 | 2026-11-22 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep a JP logo only if no official English one exists. The title logo is already English. |
| D6 | 2026-11-22 | Specs and plans | need approval, pre-approved | Pre-approved; keep going through checkpoints. |
| D7 | 2026-11-22 | Existing saves or savestates | provided, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-22 | Speaker name tag (6 cells) and location label (10 cells) draw one char a cell: names like Tsukikage, Blackburn Mts don't fit | abbreviate to 6/10 letters; engine: pack two letters a cell like C1Run | Engine (D4, pre-approved run): translate full names to the pair budget (48/80 px); phase 7 packs pairs in `C2:5641` and `C0:E1B1`. |
| D9 | 2026-11-22 | Register and sound effects | archaic fantasy; plain modern | Natural modern English, light fantasy-war flavour, archaic only for the Zodiac Gods and Sages; laughs/SFX as English interjections (glossary Rulings). Pre-approved run default. |
| D10 | 2026-11-22 | How dialogue is authored | hand-wrapped lines; paragraphs per box wrapped by tool | Paragraph per JP box (`tools/pages.py`): the tool wraps to 158 px x 3 lines and adds `{next}` boxes, headers and control codes never pass through translators (skill §Author paragraphs). |
| D11 | 2026-11-22 | Honorific forms on {hero}/{FF31} and lords (phase 6 review: "Sir {hero}", "Lady {FF31}", "-sama" and dropped どの mixed) | -sama everywhere; English titles (Sir/Lady); per-speaker mix | Under D1 (keep honorifics), pre-approved run: every suffix kept, 様 = -sama, どの/殿 = -dono, さん = -san, on names and variables alike; English titles only for word titles (陛下, 隊長). One rule the lint can enforce. |
| D12 | 2026-11-22 | Widow boxes (the wrap pushes 1-3 words of a sentence into a box of their own; 506 found) | leave (D10 allows extra boxes); fit pass rewording each page; engine (a 4th line) | Fit pass, page by page by hand (no scripted rewording): tighten to 3 lines or end the box at a sentence boundary; `batches.py widows` lists them. The box has 3 lines, so no engine fix. Pre-approved run (D6), so not asked. Done 2026-11-22 (fit01-fit03): 0 widows, and `check` now fails on any widow box. Recurring Zodiac statue speeches use one wording everywhere (the fit01 lines). |
