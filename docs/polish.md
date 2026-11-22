# Polish pass (Minors deferred from review; release refuses while any line is unticked)

- [ ] 24E4A4 - "That I, of all beings, should fall!" reads stiff; maybe "That I should be defeated!"
- [ ] 28449F - JP shows a literal placeholder ○○○○ as the item name ("It says it's a ****!"); check in game what
  the shop scene really shows and match it
- [ ] 25C52E, 278CA8 - two narration blocks share one page with no {next} in the JP (an ending variant follows
  straight on); English keeps a `\n` there: check the box flow in game
- [ ] 290558, 290B80, 2949B2 - the tutorial names commands "Deploy", "Start Battle", "Retreat" and "MAP": when the
  battle menus (side tables) are translated, make the labels match these words (or reword the tutorial)
- [ ] 28CA75 - the JP's first page has no closing 」 (a game typo); the English keeps the open quote only
- [ ] 2A7F9A..2A8036 - speakers ××××/○○○○ are JP placeholder names (unused unit slots?); English uses "****":
  check whether any scene reaches them
- [ ] 2A957C..2A9D28 - {FF12} ring shouts kept to one 3-line box each (the JP fits one); check one on screen
- [ ] 24F91E - narration pages drop the JP blank first line before 「神暦..」/「神祖連邦オルドバ」; check the layout in game
- [ ] Class しかいせん is "Immortal" in classes.json (80 px) and the ceremony line 1DF581, but the glossary's 屍解仙 =
  "Corpse Immortal" (boss; description 0EFBF0 uses it): pick one name for both
- [ ] Shop menu 1AF5A7 Buy/Sell/Quit and every Yes/No (`FF0E:0003` gaps): the English words are a cell longer than
  買う/はい, so each later option starts a cell right of its FF09 cursor slot; check the cursor in the shop (phase 8)
- [ ] 1AF628 (shop re-greeting after a cursor table) keeps the JP 「: the entry is cursor data + text, left in place
- [ ] Ceremony stat-up lines 1DF0CF.. print "{name}: Attack +{n}!" (1DF0B9 = "!"), and 1DF4C7.. "Dragon Knight open
  to {name}" (one 28-cell row); see them on a level-up / class-change screen
- [ ] Menu grid strings (b057/b064/b058): 2-cell slices force Itm, Tac, Inf, Gdr, Sg., Fld, Bin, Trd, Wp., Int, Spr;
  phase 7 (D4 engine first): widen those tilemap slices (or move the labels to more slots) and re-run
  `tools/grid.py fill` from `script/grid_specs.tsv` with full words (Items, Info, Magic, Spirit, Sign...). The
  tutorial's "choose Information" (279CA6) must match the 情報 label then
- [ ] Fragment pools 01C60C (target prompt) and 01CC4A (item window sentences) were translated one fragment per JP
  word: check on screen how the game combines them (phase 8, `tools/re/slices.py` on the English build)
- [ ] Objectives (b059) keep their JP length (no reader found): "SorcGen", "SorcCapt", "M.God 1"; if a reader turns
  up, relocate the table (D8:FC9C pointers) and write full sentences
- [ ] Status screen: the gender value 男/女 and the default hero name ソード are still JP (tile/graphic or save data)
- [ ] Place names, label vs dialogue (phase 6 review, Minor 9): labels "Blackburn Mts", "Atlas Mts",
  "Gibraltar Str.", "Rhipaean Mts" (locations 00CDA3, 00D023, 00CFBF, 00CE93); dialogue spells them out
  ("Blackburn mountains" in 1E01E0 lowercase, "Strait of Gibraltar"). After D8 pair packing (phase 7) give the
  labels the full names and add label/dialogue forms to the glossary Places table so the lint keeps them consistent
- [ ] Independent review b001-b016 (minors): class 0BFA3E しかいせん = "Immortal" (glossary 屍解仙 "Corpse
  Immortal"; widen if the field allows); item 1AE963 ペルセポネの箱 = "Persephone" (drops "Box"); 24E242 ううん
  rendered "Mm-hm" (it contradicts his "Not yet": "No, no..."); 1E1176 "Old memories of {hero}" reads as memories
  about him (the fairy speaks to him: "Your old memories are buried here...")
- [ ] Independent review b017-b032 (minors): shouts use the 80 px spell-table short forms "1000 Arrows" (258768,
  サウザンドアロー) and "Earth Dragon" (2589E8, 地竜逆撃 drops "Counter"): give the dialogue the full names
  ("Thousand Arrows", "Earth Dragon Counter") or widen the spell field; 2165A6 当たらなければどうという事はない is a
  famous quote, "If they don't hit you, it's nothing!" could be punchier ("Can't hurt you if it doesn't hit!");
  25BA86 古代人の悪霊 "the evil spirit of an ancient people" is one ancient man's ghost; 25E1A8 page 3 (what the girl
  taught him) reads as "you" believing; 2763B0 "For the first time, I thought so." is vague (he first wished he
  could carve open fate); 281A49 "Hey, or you there, or kid" (quote the three forms of address)
- [ ] Independent review b033-b036 (minors): 285161 "now it was a forgotten, dying country" (tense: "had become");
  2890B1 闘将どの "Lord Warlord" reads oddly ("Warlord-dono" per D1, or "my lord Warlord"); 287555 "You avenged
  our village, and well done..." ("Well done, I tell you..."); 28ACD3 このマウザー "I, Mauser," could be "the great
  Mauser" (style reference)
