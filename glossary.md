# Glossary - Bounty Sword

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces every table row: when the JP term is in a line, one of the EN forms must be too
(forms separated by ` / `), and no Avoid spelling may appear.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Name-san). Name order: Western (given name first).
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
| ウラヌスの指輪 | Uranus Ring | | | |
| ポセイドンの指輪 | Poseidon Ring | | | |
| 封魔石 | stone / Stone | | sealing stones (Fire Stone...) | |
| アンデッド | undead / Undead | | | |
| キャンプ | camp | | | |
| 作戦指示 | orders | | camp command | |
| 精霊水 | Spirit Water | | item | |
| 機神 | Machine God | | ancient weapons (超機神 too) | |
| 神の代理人 | agent of the gods / agent of us twelve gods | | what the Zodiac Gods call the hero | |
| 屍解仙 | Corpse Immortal | | boss at the Abadan River | |
| 悪霊 | evil spirit | | Ruins Town ghost | |
| ワルキューレ | Valkyrie | | Rune's Valkyrie Corps | |
| 火竜 | fire dragon | | Salamander | |
| スカルナイト | Skull Knight | | | |
| 報奨の剣 | Sword of Bounty | | the legendary sword that breaks the dark wall | |
| 暗黒十二神 | Twelve Dark Gods | | bound together = the ultimate weapon | |
| 閃光のシュタイア | Steyr the Flash | | | |
| 寸断のリュウビ | Ryubi the Shredder | | | |
| ロシィ | Rossy | | Steyr's sister | |
| 合体攻撃 | Combined attack | | combo shouts in caps (GIGA SMASHER!) | |

## Decisions from earlier batches
- b001-b009 (wave 0, name tables): see the tables above; short forms where the field is 48 px (B.Knight,
  B.Master, N.Master, N.Mancer, D.Knight, L.Trap, Darklord) and constellation fields 40 px (Sagitt., Capri., Aquar.).
- [00AB] is 岬 (cape): Cape Iberia, Sword Cape.
