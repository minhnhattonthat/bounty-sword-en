# Polish pass (Minors deferred from review; release refuses while any line is unticked)

Every line below was resolved in session ae (2026-11-23) unless it says otherwise. "Kept" lines are deliberate,
with the reason; the two engine limits are listed as known issues in README.md.

- [x] 24E4A4 - "That I, of all beings, should fall!" reads stiff. Now "To think that I would be defeated!"
- [x] 28449F - JP shows a literal placeholder ○○○○ as the item name ("It says it's a ****!"). Kept: the ○○○○ is in
  the game's own script (a gag, not a variable), so "****" is the faithful rendering.
- [x] 25C52E, 278CA8 - two narration blocks share one page with no {next} in the JP. Seen in game
  (`tools/debug/msgpages.py 25C52E`): the 4th line spilled into its own box as `""Our battle is over."` (doubled
  quote); page 5 is now `...war...\nOur battle is over.` -> its own box `"Our battle is over."`. 278CA8 page 4 is
  three lines in one box (`"Little time was left."` / `"The power of the Bounty Sword..."`): no spill.
- [x] 290558, 290B80, 2949B2 - tutorial command names. The deploy menu labels are "Set" / "Land" / "Fight!", the
  battle menu's is "Flee": 290558 now says 'Set' and 'Fight!', 290B80 already said 'Flee', 2949B2's "retreat" is the
  plain verb. "MAP" stays (the JP uses the Latin word and the screen label CLEAR MAP is graphic).
- [x] 28CA75 - the JP's first page has no closing 」 (a game typo). Kept as in the JP.
- [x] 2A7F9A..2A8036 - speakers ××××/○○○○ are JP placeholder names. Kept as "****" (the game's own placeholders).
- [x] 2A957C..2A9D28 - {FF12} ring shouts kept to one 3-line box each: `batches.py fit` gives 3 lines for every
  shout, including the two rewritten to "The power of Aphrodite/Pluto dwells within!" (now like the other ten).
- [x] 24F91E - narration pages drop the JP blank first line before 「神暦..」/「神祖連邦オルドバ」: the JP blank line
  plus one title line is two lines; the English titles wrap to two lines, so the page height is the same. Kept.
- [x] Class しかいせん "Immortal" vs glossary 屍解仙 "Corpse Immortal": glossary now gives both forms, "Corpse
  Immortal" in dialogue and descriptions, "Immortal" in the 80 px class field, the 48 px unit name and the
  28-cell ceremony row.
- [x] Shop menu 1AF5A7 Buy/Sell/Quit and every Yes/No: the phase 8 tours (town_item_shop, town_weapon_shop, sheets
  read ok twice) show the cursor beside each option. Kept.
- [x] 1AF628 (shop re-greeting after a cursor table) keeps the JP 「: it draws as the English font's open quote.
- [x] Ceremony stat-up lines 1DF0CF.. "{name}: Defence +{n}!" and 1DF4C7.. "Dragon Knight open to {name}": the
  longest, "Dragon Knight open to " is 22 cells + a name of at most 6 cells (the name-entry buffer $7E4D1B) = 28,
  the row width. Kept.
- [x] Menu grid strings (b057/b064/b058): 2-cell slices force Itm, Tac, Inf, Gdr, Sg., Fld, Bin, Trd, Wp., Int, Spr.
  Deferred as a known issue (README): the slices come from tilemaps the menu code builds; no tilemap data for them
  is in the ROM (searched for the camp rows' tile words) and the window scripts (C8:ECB3, C8:EFB4..) only draw the
  strings and DMA them. The tutorial 279CA6 now says "choose 'Inf'" to match the label.
  (session ak, D19: the tilemaps are C5 layout records and the frames C1 window defs, `docs/re/vwf.md` "Widening a
  menu slice". Full words now: camp Party/Formation/Status, Items x3, Use/Trade/Drop, world map Info. Left: battle
  command windows 01CA4B/01CAAB/01CAF0, cancel labels 01C5AA, target prompt "Fld" 01C60C, unit item window 01C894,
  sell tabs 01D31B, the vault jigsaw in 01CC4A (Bin, Wp., No; titles built from の/誰/が cells).)
- [x] Fragment pools 01C60C (target prompt) and 01CC4A (item window sentences): shown in the phase 8 tours and
  textcover (0 failing); the sheets were read ok.
- [x] Objectives (b059) keep their JP length (no reader found): "SorcGen", "SorcCapt", "M.God 1". Kept until a
  reader turns up.
- [x] Status screen: the gender value 男/女 and the default hero name ソード are still JP (tile/graphic or save data)
  (done: name "Sword" via `script/default_names.tsv`, session l; gender ♂/♀ via byte patch 018AA9, session q)
- [x] Place names, label vs dialogue: labels "Blackburn Mts" / "Rhipaean Mts" are 10-cell tag labels; dialogue
  now "the Blackburn Mountains" (1E01E0, 1E02EA capitalised); both forms in the glossary Places rows.
- [x] Independent review b001-b016: Immortal (above); 1AE963 ペルセポネの箱 kept "Persephone" (80 px field, the
  description names the box); 24E242 "No, no. You really are..."; 1E1176 "{hero}, your old memories are buried
  here, aren't they..."
- [x] Independent review b017-b032: 258768 "...Sure-shot arrows... Thousand Arrows!", 2589E8 "Earth Dragon
  Counter", 2165A6 "Can't hurt you if it doesn't hit!", 25BA86 "an ancient man who died a thousand years ago",
  25E1A8 p3 "That we act because we ourselves believe it...", 2763B0 "It was the first time I had ever wished for
  that.", 281A49 "'Hey,' 'you there,' 'kid'..."
- [x] Independent review b033-b036: 285161 "it had become a forgotten, dying land", 2890B1 "Warlord-dono", 287555
  "Well done, I tell you...", 28ACD3 "The great Mauser doesn't flinch..."
- [x] Independent review b037-b050: 2916E0/29571A "Maybe some other time...", 292E42 "Gh... aah... uhh...!?",
  29352E "headed", 296914 "What a brat!", 29C87E "But you couldn't kill me, could you?", 2A8BCE "Curses!",
  2A99C2/2A9A80 "The power of X dwells within!", 2AD998 "We've finally made it!"
- [x] Independent review b051-b069: British spellings throughout (Defence in ceremony/level-up/descriptions,
  Samurai Armour, armour, rumour, travelling, realised); 0EF856 "HP and SP, cures ailments"; 0EFA0E "freezes all
  others, friend and foe"; 0EFCAA "A whistle found on Volcano Isle."
- [x] Phase 6 review: the old woman's lines (215E30, 216008, 2AAF72) get "dearie" / "so they say" / "you see";
  25F62E "Mister Small-Time Bounty Chaser!" (capitalised like the others)
- [x] Engine B rows (shop box, ceremony) are one char a cell: narrow letters leave gaps ("Wel come", "Qui t").
  Deferred as a known issue (README): it needs a proportional mode in engine B. **Fixed 2026-11-23 (D18)**: engine
  B VWF (`docs/re/vwf.md`), README line removed.
- [x] jp_left C4 names (done, session ae: a whole-ROM scan for op 16/64 + a 6-word name found 11 such records, among
  them 043F2F 海兵隊長 and 04E8B3 ロブン; all 11 written in English through `script/default_names.tsv`; jp_left 0)
- [x] Story pass (session af, read-only self review, 18 chapters): 295E4C hero repeats his line of ten years ago;
  now word for word 24E502 ("Go back to your grave, you monster of evil black magic!").
- [x] 29C3BA / 29C4DA Ajax and the hero repeat their duel words of ten years ago; now match 24EF74 / 24EF38
  ("Our paths will be decided by the sword! Isn't that right, ...?! No... Master of Swords!", "...which path").
  29C1F8 なあ "Hey, {hero}..." as in the prologue.
- [x] Zodiac statue opener (11 copies) "Thou who standest before me... art thou the one..." (the statues use thou).
- [x] 297B5C Mauser keeps his "the great Mauser" boast; 271A36 "fighter of Oceanus" (the other four agree).
- [x] No contractions for Elysion (25B592), Miranda (28E0D5), Robun (297CA6).
- [x] 1E3964 / 28CA75 open quote on a page with no close: kept, the JP pages lack the closing 」 too.
