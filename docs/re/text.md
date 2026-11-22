# Text: encoding, engines, pointers

Addresses: CPU `$BB:AAAA` (HiROM, file offset = `addr & 0x3FFFFF`) or file offset `0xNNNNNN`.

## Encoding (verified)

- **16-bit little-endian codes**, one word per character, no compression, no Shift-JIS. Verified: relative search
  found ファイル at 0x1CD2A etc. (`relsearch.py --width 2`, kata_jis base 0x0171), and decoding the intro string
  エウロペアの…にもとづき at 0x1DEC37 matches the in-game shot (`work/qa/orig_new/f000800.png`).
- Code ranges (`tools/mktbl.py` builds `tbl/jp.tbl` from these):
  - `0x0001-0x005E` JIS row 1 symbols, code = JIS cell - 0x20: `03`=。 `04`=，(used as 、) `09`=？ `0A`=！
    `1D`=ー (JIS ―, the script's long vowel) `36`/`37`=「」 `53`=％ `55`=＆. Verified against the font sheet.
  - `0x00C0-0x00C9` ０-９, `0x00D1-0x00EA` Ａ-Ｚ, `0x00F1-0x010A` second Latin set (lowercase slot). Verified (YESNO,
    0123456789 in the file-menu block at 0x1CD4C).
  - `0x0111-0x0163` hiragana ぁ-ん (JIS order), `0x0171-0x01C6` katakana ァ-ヶ. Verified (しますか, ロード, を).
  - `0x0400` = two-dot leader (‥), written in pairs. Verified visually (「‥‥マクベス‥‥か‥」).
  - **Kanji**: codes `0x20-0x2F`, `0x60-0xBF`, `0x1C8-~0x4FF`, in no standard order (消=0x2AB 去=0x1F1 最=0x275
    初=0x2A2). Not identified yet: the next step is a code->kanji list `tbl/kanji.tsv` read off zoomed font sheets
    (`tools/font_sheet.py`) with script context, then `mktbl.py --kanji`. Some code-0x10-0x1A cells hold Latin Q-Z
    glyphs; check with the font before mapping.
  - `0x0000`: full-width space in dialogue; string terminator in menu tables (C1 bank).
- `tools/tbl.py` decodes byte-greedily; with 16-bit codes it can desync on `FF xx` words (FFFF then 00FF). The extractor
  must tokenise word by word (control word = `0xFFxx`), and only use the table for character words.

## Font (verified: draw routine traced)

- One 8x16 font, 2bpp, at `$EB:2D8C` (file 0x2B2D8C). Glyph address for code `c`:
  `$EB:2D8C + (c & 0xFFF0)*32 + (c & 0xF)*16`; that is the top 8x8 tile, the bottom tile is `+0x100`.
  Code `C1:86A9` computes it; `C1:8ECE` copies the two tiles into the WRAM tile buffers `$7E:A000`/`$7E:A200`
  (both engines draw through this font). `tools/font_sheet.py OUT.png [first] [count]` renders labelled sheets.
- Every glyph is one 8-px cell: kanji are squeezed into 8x16. English can use the same cell grid, but a VWF would
  fit far more per line (phase 5 decision).

## Engine A: dialogue script VM (main game, verified for FF15/FFFF by trace)

- Interpreter in bank C2; command dispatch at `C2:4A46`: a word `>= $FF00` indexes a table of 4-byte entries at
  `$C2:4A67` (`FF00`->C24B2F, FF01 C24D32, FF02 C24E82, FF03 C24FCE, FF04 C25092, FF05 C25168, FF06 C251B9,
  FF07 C251D6, FF08 C25290, FF09 C25291, FF0A C252A7, FF0B C25352, FF0C C253F7, FF0D C25441, FF0E C255C6,
  FF0F C25696, FF10 C256DE, FF11 C25726, FF12 C257D6, FF13 C25840, FF14 C258A3, FF15 C259B1, FF16 C25F7F,
  FF17 C25F9E, FF18 C2605F). Text reader around `C2:47AF`-`C2:48AA` (checks `FFFF` and `FF18`).
- Message shape seen everywhere (0x24FB5E): `FF15 <speaker> FFFF` then `「 text 」 FFFF`. The speaker is either a
  6-word literal name (`ダニエル__`, FF15 skips 12 bytes) or one name word (`FF1F` hero?, `FF28` heroine?, `FF31`)
  followed by FFFF. Inside the text `0000` breaks the line, `FFFF` waits/pages, `FF18` continues with the next
  speaker block. A message has no terminator of its own: it runs to the next pointer (2,292 of 2,333 end `」FFFF`).
- **Opcode table: 50 entries `FF00-FF31`** (FF28's table slot is 0, but FF28 still appears as a name word after FF15).
  The dispatcher at `C2:4A46` steps past the opcode word, then handlers read arguments at `[$48],y` (y = `$7E3727`).
  Measured from each handler (`tools/re/engA_args.py`, which reads `work/re/engA/all.txt` =
  `dis65816.py ROM C24B2F 7000 --map hirom`); verified for the common ones by tokenising all 2,333 master messages
  with no stray opcodes (`tools/re/engA_opstat.py`; stray codes it lists past 0x279F44/0x29CD3A/0x2AE85A are data
  after the last message of a block, read because the script bounds the last message at +0x400):
  - 0 args: FF00 (end), FF01-FF04, FF07, FF08, FF0D, FF0E, FF11-FF13, FF16-FF18, FF2B/FF2C (print the 3-digit
    numbers in `$7E379F`/`$7E37A1`), FF2E, FF2F/FF30 (if a flag is clear skip to after the next `FF18 FFFF`).
  - 1 arg word: FF05, FF06, FF09, FF0A, FF0B, FF0C, FF14 (`FF14 0003 FF00` closes some messages).
  - FF0F/FF10: 1-2 words (conditional); FF2D: word + two 24-bit pointers (8 bytes, conditional jump);
    FF25, FF26, FF27, FF29, FF2A read 3-7 bytes. None of these occur in the master text (FF10 once, in data past a
    block end). Read the handler again if one turns up in another table.
  - FF19-FF1E print hero-name letters 1-6 (always as the run `FF19..FF1E`); FF1F-FF24 and FF31 print other names
    (they rewind the pointer and re-enter the printer at `C2:47DA`), so they act as characters, not codes.
  - Opcodes seen in master text, with counts: FF15 2098, FF18 1569, FF19-1E 377 runs, FF28 487, FF1F 437, FF31 134,
    FF2F 132, FF30 120, FF12 90, FF00 35, FF04 16, FF14 12, FF2B 7, FF2C 1.

## Engine B: intro / ceremony script VM (verified by disassembly)

- Interpreter `C3:C6BF`: reads words via `C3:C789`; `>= $FF00` dispatches through the word table at `$C3:C763`.
  Script pointer at `$7E:4A37/39`, offset `$7E:4A35`. Used by the opening ceremony at `$DD:EBCF` (file 0x1DEBCF..~0x1DF59B).
- Opcodes and argument words: FF00 end-if, FF01 newline, FF02 wait key, FF03 clear box, FF04 +1, FF05 print instantly
  up to the next FFxx, FF06 +2 (call: 24-bit pointer lo-word, bank-word; return saved), FF07 return, FF08 +1, FF09 +5
  (choice: two 24-bit pointers + 1), FF0A choice resolve, FF0B +4 (indexed jump: pointer to index, pointer to a table
  of 3-byte pointers), FF0C +2 (JML to native code), FF0D end, FF0E +1 (advance cursor n cells), FF0F 0, FF10 +2
  (pointer to 2-word params), FF11 0, FF12 0. Here `0000` is a drawn space, not a newline.
- Characters are placed through a position table (`$7E:4A3D`), not a running x: line breaks are FF01.

## Pointers (verified for one entry; table bounds by zero padding)

- **Master dialogue table**: three-byte pointers (lo, hi, bank), message id = index from base **0x26D5EF**
  (`LDA $EDD5EF,x` at `C2:456E`, also `C2:CCA7`, `C6:D046/D352/D5CA`), ending 0x26F2C9: 2,457 slots. Slots 0-130 are
  zero except ids 16 (0x26D61F), 17 and 64 (0x26D6AF) (prompts at 0x26F317-0x26F3FB); the dense run of 2,333
  starts at 0x26D772 (id 131). Entry 0x26EF3F -> `$E4:FB5E` (read by `C2:47AF` when that message showed). Targets cover the big text
  blocks: 0x1E0008-0x1E8B5E, 0x214610-0x21864C, 0x24DB60-0x24FE8A, 0x257BD8-0x25FBFE, 0x27141A-0x279DEE,
  0x280F25-0x28F8D9, 0x29040C-0x29CC8E, 0x2A7D46-0x2AE7A8 (~300 KB). Pointers inside scripts (FF06/FF09/FF0B-style)
  are not counted yet.
## Text inventory (every 16-bit text run in the ROM)

`tools/re/textruns.py` lists every run of text-like words (both byte parities, >= 6 kana, master blocks excluded);
`work/re/clusters.txt` groups them. Each run was read with `tools/re/words.py`; `tools/re/refs24.py` finds 24-bit
pointers into a range, `tools/re/p24.py` prints a pointer list. Runs not listed below decode as noise (tile maps,
arithmetic tables such as 0x11B91, data at 0x21E8F6-0x256DD4 and 0x2700D0-0x270F44): not text.

| File range | Contents | Form | Read by / pointers | Status |
|---|---|---|---|---|
| 0x1E0008-0x1E8B5E, 0x214610-0x21864C, 0x24DB60-0x24FE8A (then FFFF fill to ~0x250600), 0x257BD8-0x25FBFE, 0x27141A-0x279DEE, 0x280F25-0x28F8D9, 0x29040C-0x29CC8E, 0x2A7D46-0x2AE7A8, 0x26F317-0x26F3FB | story dialogue (engine A) | message = pointer to next pointer | master table base 0x26D5EF | verified |
| 0x00CD7B-0x00D151 | map / chapter location names (ラインメタル…, イーストエンド) | 10 words fixed, index = map-1 | `C0:CB57 LDA $C0CD7B,x`, drawn by `C0:E1B1` one cell per call (chapter card) | verified (code) |
| 0x0BF8AE-0x0C0004 | class names (バウンティハンター, ソードマスター…) | 10 words fixed | 3-byte pointer list at 0x0BF800 (one per class line) | verified (table) |
| 0x1ADFEF-0x1AEDB9 | weapon / item names (ミスリルの…, エクスカリバー) | 10 words fixed (data words before the names in places) | item records at 0x2DDD2 (8-byte stride, 24-bit pointer) | guess |
| 0x1AF349-0x1AFDC2 | short strings, 0000-padded | variable, 0000 runs | many 24-bit pointers (0x22xxx, 0x83xxx) | guess |
| 0x08DF4A-0x08E9D6 | unit titles / epithets (ドラゴンバスター, …のシュタイアー) | 16 words fixed | 24-bit pointers spread in code | guess |
| 0x06E3AB-0x06E627 | unit names (ロジャー, ミランダ, シュタイア…) | 5 words fixed | `C6:E38F`, `C6:E644` | guess |
| 0x025D5D-0x025F7F | speaker name -> portrait table (ソード___ 01 18, ロジャー__ 04 17…) | 8 words: 6-word name + 2 ids | `C2:4826`.. `C2:5D25..5D61` | guess: FF15 literal names must match it |
| 0x046CF4-0x0473B0, 0x044E40 | unit/class data records with embedded names (パラディン, …マスター) | mixed records | pointer list at 0x042AE1 | guess |
| 0x01BFFF-0x01D3AB | menu strings: file menu, name-entry kana grid (0x1C285), options | 0000-terminated | 24-bit pointers in menu records (0x08E9DC-0x08F9xx, 0x05Bxxx) and code; drawn by `C1:8F16` | verified for the file menu |
| 0x04136F-0x0418E3 | save / system prompts (…しますか？) | engine B script | pointers at 0x040797-0x04135D | guess |
| 0x05E8A0-0x05EF51, 0x0073AB-0x007673 | battle prompts (どうするの？, MP が つきて…) | engine A/B style (FF09/FF11/FF12/FF14) | pointers in 0x04B8xx-0x04Dxxx, 0x05Dxxx, 0x006xxx-0x007xxx | guess |
| 0x0EE59E-0x0EFD28 | spell / item descriptions (マヒさせることもある) | engine B, FF06 calls shared fragments | 645 pointer hits, many in code | guess |
| 0x18FD06-0x18FF48 | map objectives (…MAPのはしまでたどり着け) | FFFE splits lines, FFFF ends, 0401/0402 brackets | 24-bit pointers in `C6:1221`.. | guess |
| 0x1DEBCF-0x1DF5A3 | opening ceremony, class-change lines (…に転職できます) | engine B | `$DD:EBCF` from engine B | verified (ceremony) |

Status words: verified = decoded with the reading code found; guess = decoded text and a plausible pointer site,
reader not confirmed (phase 4 confirms each with a ROM-read log before extracting it).
