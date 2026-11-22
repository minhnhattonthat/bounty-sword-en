# Glossary - Bounty Sword

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces every table row: when the JP term is in a line, one of the EN forms must be too
(forms separated by ` / `), and no Avoid spelling may appear.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics (D1): kept, hyphenated, on names and on {hero}/{FF31} alike, never swapped for an English title:
  さん -> -san ({hero}-san), 様/さま -> -sama ({hero}-sama, {FF31}-sama, Elysion-sama), どの/殿 -> -dono
  ({hero}-dono, Faust-dono), ちゃん -> -chan, くん -> -kun. Titles that are words, not suffixes, stay English
  (陛下 "Your Majesty", 隊長 "Captain"). `batches.py check` fails on a JP honorific after a name or name variable
  without its suffix. Name order: Western (given name first).
- Romanisation source: official English names, else an earlier fan patch, else Hepburn without macrons. There is no
  official English release or known fan patch; names that are real gun makers or myth names use that spelling
  (Mauser, Steyr, Detonics, Colts, Hammerli, Rheinmetall; Ares, Thetis, Erebus, Nyx).
- Credits: English.
- Register (D9): natural modern English with a light fantasy-war flavour; no archaic "thee/thou" except the Zodiac
  Gods and the Sages. Sound effects and laughs as English interjections (ククク -> "Heh heh heh...", フフフ ->
  "Hmhmhm..." / "Heh...", ゾクゾク -> "a shiver", ‥‥ -> "...").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening. Name fields that can't
  grow (unit names 48 px, items/classes/spells 80 px) use the short forms in the tables below.

## Style rules
- Punctuation: 「」 -> "..." (the page tool restores the structural 「」); 『』 -> '...'; ‥‥ -> ...; ！？ -> ?!/!?;
  ！！ -> ! (one, two at most); full stop at the end of every sentence unless it ends in ... ! or ?.
- The hero speaks as {hero} ({FF1F} as speaker): terse, dry, a professional bounty hunter, "I" (オレ) not "me".
- The fairy ({FF28}, his guide and narrator of the map hints) is chatty, teasing, motherly: "you know", "huh?".
- {FF31}: a second variable name word (the girl the hero escorts, the client of a job). Keep it inline, never
  glue a suffix or "'s" onto it; use "of {FF31}" or rephrase.
- Villains (Elysion, Gauche, the Dark Lord, Federation officers) sneer: キサマ -> "you" with venom ("you wretch").
- Old men (ジジイ, 物知りジジイ) ramble: "eh?", "my boy"; ～じゃ/のう -> "I tell you", "hm?".
- Roger: rough, hot-headed soldier. Miranda: polite, calm, uses です/ます -> no contractions, gentle. Ajax: blunt
  general. Athena: noble, soft. Tsukikage: ninja, clipped. Ryubi: cold swordsman. Mauser/Steyr/Colts/Hammerli/
  Detonics: soldiers of the rebellion.
- Numbers drawn by {FF2B}/{FF2C}: no ordinal suffix glued on ("No. {FF2B}", "{FF2B} gold").

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ロジャー | Roger | 48px | | |
| ミランダ | Miranda | 48px | | |
| ロブン | Robun | 48px | | Roben / Robin |
| マウザー | Mauser | 48px | | Mouser |
| シュタイア / シュタイアー | Steyr | 48px | | Steyer / Stair |
| ファウスト | Faust | 48px | | |
| アテナ | Athena | 48px | | Atena |
| リュウビ | Ryubi | 48px | | Ryuubi / Ryuhbi |
| ツキカゲ | Tsukikage | 48px | | |
| ルーネ | Rune | 48px | | |
| アジャックス | Ajax | 48px | | |
| ヘンメリー | Hammerli | 48px | gun maker Hammerli | Henmery / Hemmerli |
| コルツ | Colts | 48px | | Coltz |
| ハリス | Harris | | | |
| ダニエル | Daniel | | | |
| ノルン | Norn | | | |
| マクベス | Macbeth | | | |
| テティス | Thetis | | | Tethys |
| デトニクス | Detonics | | | Detnics |
| エリュシオン | Elysion | | | Elysium |
| ゴーシュ | Gauche | | | Gosh |
| ラグガドル | Raggadol | | | |
| ダークロード | Dark Lord / Darklord | | Darklord only in the 48 px unit name field | |
| レオパード | Leopard | | | |
| エレボス | Erebus | | | |
| ニュクス | Nyx | | | |
| マイア | Maia | | | |
| ボリス | Boris | | | |
| シーナ | Sheena | | | |
| ズール | Zool | | | |
| ドーン | Dorn | | | |
| ジーン | Jean | | | |
| バロン | Baron | | | |
| ザムス | Zams | | | |
| リーザ | Liza | | | |
| シルカ | Silka | | | |
| ロシィ | Rossy | | | |
| フュリス | Furis | | | |
| 黄道十二神 | Zodiac Gods / Twelve Gods / Zodiac | | speaker tag: Zodiac | |
| 大賢者 | Archsage | | | |
| 情報屋 | informer / Informer | | | |
| オフィーリア°レス°エリュシオン | Ophelia Les Elysion | | {FF31}'s real name (Elysion's daughter by his eighth wife) | |
| コウホウ | Koho | | samurai company captain, duels the hero | |
| タウルス | Taurus | | Federation assault landing platoon leader, Wolf Forest | |
| 飛王丸 | Hiomaru | | the marine captain's roc | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ラインメタル | Rheinmetall | | the kingdom; label: Rheinmetall | Rhinemetal |
| エウロペア | Europea | | the continent | Europa |
| オルドバ | Ordoba | | the Federation | Ordova / Cordoba |
| ロムルス | Romulus | | 王都ロムルス "the royal city of Romulus": a military realm allied with Rheinmetall, not its capital | |
| イーストエンド | East End | | | Eastend |
| ブラックバーン | Blackburn | | | |
| アーデン | Arden | | | |
| エルツ | Erz | | | |
| リパイオス | Rhipaean | | Rhipaean Mountains | Ripaios |
| イベリア | Iberia | | | |
| エリダヌス | Eridanus | | | |
| パドヴァ | Padova | | | Padua |
| スパニア | Spania | | | |
| タルテソス | Tartessos | | | |
| シェブール | Cherbourg | | | Sheboor |
| ミッドガルド | Midgard | | | |
| ジブラルタル | Gibraltar | | | |
| アトラス | Atlas | | | |
| アバダン | Abadan | | | |
| アルダブラ | Aldabra | | | |
| メッシーナ | Messina | | | |
| アクラ | Accra | | | Akura |
| オケアノス | Oceanus | | | |
| ヴァルハラ | Valhalla | | | |
| 水晶の入り江 | Crystal Cove | | where {FF31} washes ashore | |
| 狼の森 | Wolf Forest | | | |
| 忘れられた谷 | Forgotten Valley / valley forgotten | | | |
| 氷結の大地 | Frozen Land | | rebel fort (Silka ruins) below the Rhipaean Mountains | |
| 紅の湖 | Crimson Lake | | | |
| 悪魔の巣 | Devil's Nest | | the southern desert | |
| ハイランド | Highland | | lone island west of Rheinmetall | |
| タルテソスの門 | Tartessos Gate | | | |
| 剣のみさき | Sword Cape | | | |
| 閉ざされた島 | Isolated Isle | | the Archsage's island; location label too | |
| ヘラクレスの柱 | Pillars of Hercules | | strait between north and south Europea | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| バウンティハンター | bounty hunter / Bounty Hunter | | | |
| バウンティ°ソード / バウンティソード | Bounty Sword | | | |
| マスター°オブ°ソード | Master of Swords | | the hero's old title | Sword Master |
| 連邦 | Federation | | Ordoba Federation | Union |
| 反乱軍 | rebel / Rebel | | rebel army, the rebels | |
| ブラッドシールド | Blood Shield | | | |
| シルバーナイト | Silver Knight | | | |
| アレスの指輪 | Ares Ring | 80px | the twelve rings: "<God> Ring" | Ring of Ares |
| ヴィナスの指輪 | Venus Ring | | | |
| ヘルメスの指輪 | Hermes Ring | | | |
| セレネの指輪 | Selene Ring | | | |
| アポロンの指輪 | Apollo Ring | | | |
| マーキュリーの指輪 | Mercury Ring | | | |
| アフロディーテの指輪 | Aphrodite Ring | | | |
| プルートゥの指輪 | Pluto Ring | | | |
| ゼウスの指輪 | Zeus Ring | | | |
| クロノスの指輪 | Cronus Ring | | | Kronos |
| クロノス | Cronus | | the Zodiac God of time (時神クロノス, ceremony fragment <= 10 chars); same spelling as Cronus Ring | Chronos / Kronos |
| ウラヌスの指輪 | Uranus Ring | | | |
| ポセイドンの指輪 | Poseidon Ring | | | |
| 封魔石 | stone / Stone | | sealing stones (Fire Stone...) | |
| アンデッド | undead / Undead | | | |
| キャンプ | camp | | | |
| 作戦指示 | orders | | camp command | |
| 精霊水 | Spirit Water | | item | |
| 機神 | Machine God / M.God | | ancient weapons; numbered "Machine God No. 8"; "M.God 1" only in the fixed-length objectives | |
| 超機神 | Machine God Supreme / Machine God | | the god of destruction Elysion revives; "Machine God" only in the 80 px class field | |
| 神の代理人 | agent of the gods / agent of us twelve gods | | what the Zodiac Gods call the hero | |
| 屍解仙 | Corpse Immortal | | boss at the Abadan River | |
| 悪霊 | evil spirit | | Ruins Town ghost | |
| ワルキューレ | Valkyrie | | Rune's Valkyrie Corps | |
| 火竜 | fire dragon | | Salamander | |
| スカルナイト | Skull Knight / Skull Kn. | | "Skull Kn." only in the fixed-length objectives | |
| 報奨の剣 | Sword of Bounty | | the legendary sword that breaks the dark wall | |
| 暗黒十二神 | Twelve Dark Gods | | bound together = the ultimate weapon | |
| 閃光のシュタイア | Steyr the Flash | | | |
| 寸断のリュウビ | Ryubi the Shredder | | | |
| ロシィ | Rossy | | Steyr's sister | |
| 合体攻撃 | Combined attack / Combo | | combo shouts in caps (GIGA SMASHER!) | |
| 賞金かせぎ | bounty chaser / bounty hunter | | {FF31}'s slight ("bounty chaser"), Thetis corrects her: "Bounty HUNTER!"; the hero and Colts use it of themselves | |
| ニンジャマスター | Ninja Master | | Tsukikage's title | |
| ドラゴンバスター | Dragon Buster | | Mauser | |
| 暗黒の結界 / 暗黒のカベ | barrier of darkness / wall of darkness / Dark Wall | | around the Federation's royal city | |
| 封印の墓所 | Sealed Tomb | | northern tip of Rheinmetall | |
| 悪神の代理人 | agent of an evil god | | Macbeth | |
| 不敗の聖騎士 | Undefeated Paladin | | the hero's old epithet | |
| 味方殺し | comrade-killer | | what the kingdom calls the hero | |
| 闘将 | Warlord | | Ajax's title; Roger also calls the Dark Lord this | |
| 竜騎士団 | Dragon Knights | | 連邦竜騎士団 "Federation Dragon Knights", Spania Plateau | |
| 叫びのフエ | Shriek Whistle | 80px | confuses the Hydra (item name) | Screaming Flute |
| ハイドラ | Hydra | | three-headed super-heavy weapon at Tartessos Gate | |
| 超黒の魔導士 | Ultra-Black Sorcerer | | Faust's epithet | |
| 機動トウテキ隊 | Mobile Grenadier Corps | | Steyr's Romulus army unit | |

## Decisions from earlier batches
- b001-b009 (wave 0, name tables): see the tables above; short forms where the field is 48 px (B.Knight,
  B.Master, N.Master, N.Mancer, D.Knight, L.Trap, Darklord) and constellation fields 40 px (Sagitt., Capri., Aquar.).
- [00AB] is 岬 (cape): Cape Iberia, Sword Cape.
