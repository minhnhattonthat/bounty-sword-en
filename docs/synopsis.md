# Synopsis (built from the extracted script; extend it as batches are translated)

No guide or wiki was used: everything here is read off `script/`. Mark a fact "(guess)" until a later batch confirms it.

## Who is who
- **Hero** (default name Sword, player-named: `{hero}`, speaker `{FF1F}`): a bounty hunter who once bore the title
  "Master of Swords" and threw the name away. Terse, dry, says little about his past.
- **The fairy** (speaker `{FF28}`, name word): his long-lived companion; gives the map hints ("This is East End...")
  and comments on every place. Chatty, teasing, jokes about being old ("I sound like a granny").
- **`{FF31}`**: a second variable name; the girl the hero meets at Crystal Cove and who is kidnapped by the Dark Lord
  at the Strait of Gibraltar (guess: the "Saint of the Frontier"). Also used for the client in job prompts.
- **Rebel army** (反乱軍): Roger (rowdy), Miranda (calm, polite; Roger's old friend), Robun, Mauser, Steyr,
  Colts, Hammerli, Detonics; first met in the Frozen Land.
- **Kingdom of Rheinmetall**: an island kingdom north of the continent of Europea (its port town is the only
  gateway to the continent); Ajax (general), the Minister of War. **Romulus** ("the royal city of Romulus") is a
  separate military power allied with Rheinmetall after the war ten years ago; the Federation destroyed it first.
- **The fairy is Thetis** ({FF28}; the hero calls her "Thetis" at the first Zodiac statue).
- **Rune** (Athena's older brother; speaks partly in a feminine register) commands the Federation's Valkyrie Corps;
  Athena (a Silver Knight of their fallen small homeland) swears to strike him down.
- **Ordoba Federation** (連邦): the expanding enemy power; soldiers, officers, airborne troops; uses "Machine God"
  ancient weapons late in the game.
- **Zodiac Gods** (黄道十二神): sealed powers; twelve rings (Ares Ring ... Poseidon Ring) to be gathered and bound
  into one; they name the hero their agent.
- **Villains**: the Dark Lord, Elysion, Gauche, Raggadol, Erebus and Nyx; Faust (a cultist chanting to dark gods,
  also scouted by the Federation).
- Others: Athena, Tsukikage (ninja), Ryubi (swordsman, "the Shredder"), Rune, Thetis, Norn, Macbeth, Daniel.

## Prologue (master_24DB56, translated b010-b011)
- Year 4095 of the Divine Calendar: the Divine Federation of Ordoba invades Europea from the south; seven nations
  fall; Rheinmetall (far north) is next.
- Ten years ago the hero, "the Undefeated Paladin" / "Master of Swords", fought in Rheinmetall's 17th Independent
  Knight Brigade with Ajax, Norn, Daniel and Macbeth; they beat the Zombie Master Raggadol ("all that awaits you is
  nothingness"). The fairy ({FF28}) was with him then (he had rescued her from confinement).
- The brigade learned it was a sacrificial decoy. Daniel left; Ajax dueled the hero to stop him going back to save
  the main force (scars: the hero's cheek, Ajax's left eye) and left; Norn went with the hero and died shielding him;
  the kingdom blamed the hero for the main force's loss. He drifted for ten years.
- Now: Thetis (his partner, takes the jobs, cheerful nagging) wakes him in a tavern: a job from the Rheinmetall
  knights via Minister Macbeth, wipe out the bandits in East End (100G up front).

## Mid game (master_1E0000, b012-b016)
- Map hints by Thetis for every location (b012-b013), then: the Ruins Town (the Fallen City) at Europea's southern
  tip, an evil spirit guarding "my father's legacy"; Faust reads ancient inscriptions about the gods' weapons and
  twelve children (Ordoba, Romulus, Rheinmetall, Iberia, Atlas, Rhipaean...) given the Zodiac rings to seal.
- Zodiac statues name the hero "agent of the gods": bind the twelve rings into one.
- Accra: Rune's Valkyries stall the rebels with Machine God No. 8. Aldabra Island: the fire dragon Salamander (the
  informer's job). Ship to the Isolated Isle (marines attack on the way): a 100,000-year-old boy holds the
  Poseidon Ring; with all twelve, go to the four sages of the Sage Village below the Rhipaean Mountains.

## Structure
- Scenarios are map battles (objectives per scenario, table `D8:FC9C`), with town/camp scenes between them.
- Map hints by the fairy per location: "This is <place>. We haven't cleared it yet." / memories once cleared.
