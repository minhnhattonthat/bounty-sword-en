"""Write tools/debug/scenes.tsv (the debug warp's scene list). Edit the lists here, then run:

    python -X utf8 tools/debug/make_scenes.py && python -X utf8 tools/debug/warp_all.py --sheet

Columns (read by tools/debug/warp.lua): name kind map mode msg expect hold frames route mash then sav note.
"sav" is read by warp_all.py only: a battery save (repo-relative) to boot with, made by tools/debug/save_test.py.
Scenario numbers and labels come from the leftover SCENARIO select (C0:DBAA, "01:A-01".."59:A1R-"); see docs/re/debug.md.
"""
from pathlib import Path

OUT = Path(__file__).with_name("scenes.tsv")
COLS = "name kind map mode msg expect hold frames route mash then sav note".split()

LABELS = {n: lab for n, lab in enumerate(
    "- A-01 A-02 A-03 A-04 A-05 A-06 A-07 A-08 A-09 A-10 B-01 B-02 B-03 B-04 B-05 B-06 B-07 B-08 B-09 B-10 B-11 "
    "B-12 B-13 B-14 B-15 B-16 CEX DEX - B-17 C-01 C-02 C-03 C-04 C-05 C-06 C-07 C-08 C-09 C-10 C-11 C-12 C-13 C-14 "
    "C-15 C-16 EEX FEX GEX B-4B B-1B - - C-17 C-18 C-19 C-20 AEX A1R".split())}
UNUSED = {29, 52}            # select loads nothing (blank labels); 53 is blank too but plays a card and a map
TOWN = {1, 27, 28, 47}       # end in mode 13 (town / event scene), no briefing or card
NO_CARD = {37} | TOWN        # 37 goes straight to its map
CARD_LAST = set()            # 24, 33, 59 play an event scene after the card; with A mashed they reach the map too

# boot route: Pioneer logo, intro (Start at f1500 skips it), title by ~f2200, Start opens the file menu
BOOT = "1500 -;6 start;700 -;6 start;400 -"


def route_len(spec):
    return sum(int(s.split()[0]) for s in spec.split(";")) if spec else 0


def row(**kw):
    r = {c: "" for c in COLS}
    r.update({k: str(v) for k, v in kw.items()})
    # the proof shot comes `hold` frames after the expected mode: let the queued inputs finish first
    need = max(route_len(r["route"]), route_len(r["then"])) + 250
    if r["kind"] != "boot" and (r["route"] or r["then"]):
        r["hold"] = str(max(int(r["hold"] or 0), need))
    return r


def steps(*parts):
    return ";".join(p for p in parts if p)


def downs(k, gap=40, hold=6):
    return ";".join(f"{hold} down;{gap} -" for _ in range(k))


def scenes():
    out = [
        row(name="intro", kind="boot", hold=1400, note="cold boot: Pioneer logo and the opening intro"),
        row(name="title", kind="boot", hold=2400, route="1500 -;6 start", note="title screen, PUSH START BUTTON"),
        row(name="filemenu", kind="boot", expect=3, hold=300, route=BOOT, note="3-slot file menu"),
        row(name="load_file2", kind="boot", expect=6, hold=400, frames=8000, sav="work/saves/edit_map45.srm",
            route=steps(BOOT, "6 a;80 -;6 down;40 -;6 a;80 -;6 a;80 -"),
            note="needs --sav with a used file 2: the cursor starts on Load when a save exists; Load -> file 2 "
                 "-> camp (tools/debug/save_test.py)"),
        row(name="ceremony", kind="boot", expect=17, hold=700, frames=9000, route=steps(BOOT, "900 -;6 start;30 -;6 a;60 -"),
            note="New Game: opening ceremony (engine B text)"),
        row(name="prologue", kind="boot", expect=13, hold=500, frames=12000,
            route=steps(BOOT, "900 -;6 start;30 -;6 a;60 -"), mash="a,a,a,start:45",
            note="New Game through the ceremony and its name entry into the first town scene (master text)"),
        row(name="name_entry", kind="mode", map=1, mode=19, expect=19, hold=450, note="name entry screen (mode 19)"),
        row(name="narration", kind="mode", map=2, mode=15, expect=15, hold=300,
            note="narration text screen (mode 15; same text for every map tried); continues to the camp"),
        row(name="worldmap", kind="mode", map=31, mode=8, expect=8, hold=500, note="world map with location label"),
        row(name="gameover", kind="mode", map=31, mode=12, expect=12, hold=200, note="GAME OVER"),
        row(name="to_be_continued", kind="mode", map=31, mode=11, expect=11, hold=200, note="TO BE CONTINUED!"),
        row(name="credits", kind="mode", map=31, mode=18, expect=18, hold=2500, note="staff roll (mode 18)"),
        row(name="demo", kind="mode", map=2, mode=2, expect=2, hold=600, note="attract demo battle (mode 2)"),
        row(name="mode09", kind="mode", map=31, mode=9, expect=9, hold=300,
            note="mode 9 (C1:B15F): spell-like sequence, garbled out of context, returns to boot; not identified"),
        row(name="msg", kind="msg", map=37, msg=131, expect=7, hold=300,
            note="any master message: --var MSG=<id> swaps it into scenario 37's first dialogue"),
    ]
    camp = ["party", "orders", "items", "resolve", "map", "config", "file"]
    for k, sub in enumerate(camp):
        out.append(row(name=f"camp_{sub}", kind="mode", map=31, mode=6, expect=6, hold=600,
                       route=steps("300 -", downs(k), "6 a;200 -"), note=f"camp menu -> {sub}"))
    out.append(row(name="camp_save", kind="mode", map=31, mode=6, expect=6, hold=1400,
                   route=steps("300 -", downs(6), "6 a;200 -;6 a;200 -;6 a;200 -;6 a;300 -"),
                   note="camp -> file -> save -> file 1 (writes SRAM: the run's .srm is a game-written base save)"))
    out.append(row(name="camp", kind="mode", map=31, mode=6, expect=6, hold=400, note="camp menu (mode 6)"))
    out.append(row(name="camp_party_status", kind="mode", map=31, mode=6, expect=6, hold=800,
                   route=steps("300 -;6 a;200 -", downs(1), "6 a;200 -;6 a;200 -"), note="party -> status"))
    # town menu: weapon shop, item shop, tavern, party, items, leave town. After the warp the game used to freeze on
    # an APU handshake (C2:F5A2; it looked like ignored input): warp.lua now nudges it, see APU_NUDGE in the log.
    # Party/items/leave = camp screens and world map.
    town = ["weapon_shop", "item_shop", "tavern"]
    out.append(row(name="town_menu", kind="scenario", map=1, expect=13, hold=560, route="",
                   note="town (A-01) command menu (town_menu table 0396B2: Arms, Items, Tavern, Party, Pack, Leave)"))
    for k, sub in enumerate(town):
        out.append(row(name=f"town_{sub}", kind="scenario", map=1, expect=13, hold=600 + 300 * (k == 2), route="",
                       then=steps("500 -", downs(k, 60, 16), "6 a;300 -"), note=f"town (A-01) menu -> {sub}"))
    # tavern -> "Look for allies" -> "Got it!" (05E8F8, FF03 runs on) -> roster greeting 05E954 -> roster list
    # (battle_prompts, tools/byte_scripts.py: FF26 skips, FF25 count, FF27 choice)
    out.append(row(name="town_tavern_roster", kind="scenario", map=1, expect=13, hold=1500, route="",
                   then=steps("500 -", downs(2, 60, 16), "6 a;300 -;6 a;120 -;6 down;60 -;6 a;300 -;6 a;200 -;6 a;300 -"),
                   note="town (A-01) tavern -> Look for allies -> roster greeting -> roster list"))
    # shop flows (dialogue in short_strings 1AF585..1AFDC2): Buy -> item -> price confirm; Sell; trade-in confirm
    shop = "500 -;6 a;300 -"
    flows = {"buy": (steps(shop, "6 a;200 -;6 a;400 -"), 1100, "Buy -> Iron Sword -> price Yes/No"),
             "sell": (steps(shop, "6 right;40 -;6 a;400 -"), 1100, "Sell -> what'll you sell"),
             "trade": (steps(shop, "6 a;200 -;6 a;200 -;6 a;200 -;6 down;60 -;6 a;200 -;6 a;200 -"), 2000,
                       "Buy -> Iron Sword -> Yes -> Steel Sword -> trade-in price Yes/No")}
    for sub, (then, hold, note) in flows.items():
        out.append(row(name=f"shop_{sub}", kind="scenario", map=1, expect=13, hold=hold, route="", then=then,
                       note=f"weapon shop: {note}"))
    # A presses through the opening lines: the English build pages 12 times (the JP ROM 10; 12 there opens Party,
    # so the old work/qa/tour_jp battle proofs were made with 10). 12 and 13 both land on the command menu.
    skip = "300 -" + ";6 a;60 -" * 12 + ";400 -"
    out.append(row(name="battle_menu", kind="scenario", map=37, expect=7, hold=1300, then=skip,
                   note="battle map command menu (party / items / withdraw) after the opening lines"))
    for k, sub in enumerate(["party", "items", "withdraw"]):
        if sub == "party":  # the route lands back on the map; battle_status covers the unit screen
            continue
        out.append(row(name=f"battle_{sub}", kind="scenario", map=37, expect=7, hold=1800,
                       then=steps(skip, downs(k), "6 a;300 -"), note=f"battle command menu -> {sub}"))
    out.append(row(name="battle_status", kind="scenario", map=37, expect=7, hold=2000, mash="a:40",
                   note="unit status on the battle map (A mashed)"))
    # Scenario 11 (B-01) starts with the deploy menu (X: Set/Land/Orders/Fight!); after Fight!, X starts a move
    # order and C4:18F1 draws move_prompt 0419DC in the top-right box.
    # The first X lands back on the deploy menu (cursor on Set); B, up (wraps to Fight!), A starts the battle, and
    # the last X opens the prompt (session aa: without the tail, C4:193D never ran in a cold-boot tour).
    out.append(row(name="battle_move", kind="scenario", map=11, expect=7, hold=3500,
                   then=steps(skip, "6 b;60 -;6 x;100 -;6 down;40 -;6 a;900 -;6 x;150 -",
                              "6 b;60 -;6 up;30 -;6 a;300 -;6 x;150 -"),
                   note="B-01: deploy menu -> Fight! -> X: move order prompt (move_prompt 0419DC)"))
    for n in range(1, 60):
        if n in UNUSED:
            continue
        lab = LABELS[n]
        if n not in NO_CARD:
            out.append(row(name=f"card_{n:02d}", kind="scenario", map=n, expect=14, hold=300,
                           note=f"scenario {n} ({lab}): briefing then chapter card"))
        expect = 13 if n in TOWN else 14 if n in CARD_LAST else 7
        out.append(row(name=f"scen_{n:02d}", kind="scenario", map=n, expect=expect, hold=600, mash="a:40",
                       note=f"scenario {n} ({lab}) opening"))
    return out


def main():
    rows = scenes()
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names)), "duplicate scene names"
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(COLS) + "\n")
        for r in rows:
            vals = [r[c] for c in COLS]
            assert all("\t" not in v and "\n" not in v for v in vals)
            f.write("\t".join(vals) + "\n")
    print(f"{OUT}: {len(rows)} scenes")


if __name__ == "__main__":
    main()
