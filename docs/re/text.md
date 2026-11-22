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
- Message shape seen everywhere (0x24FB5E): `FF15 <speaker> FFFF` then `「 text 」 FFFF`. The speaker is either a name
  in kana (テティス + padding words 0000) or a word like `FF1F`/`FF28` (a name/portrait id: guess). Inside the text
  `0000` breaks the line, `FFFF` waits/pages, `FF18` continues with the next speaker block.
- **Argument counts per opcode: not yet measured** (guess: most take 0). Before extraction, read each handler for
  `LDA [$48],y`/`INY INY` pairs, as done for engine B below. A wrong count desyncs everything after it.

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

- **Master dialogue table**: 2,333 three-byte pointers (lo, hi, bank) at file **0x26D772-0x26F2C9**, zero padding on
  both sides. Entry 0x26EF3F -> `$E4:FB5E` (read by `C2:47AF` when that message showed). Targets cover the big text
  blocks: 0x1E0008-0x1E8B5E, 0x214610-0x21864C, 0x24DB60-0x24FE8A, 0x257BD8-0x25FBFE, 0x27141A-0x279DEE,
  0x280F25-0x28F8D9, 0x29040C-0x29CC8E, 0x2A7D46-0x2AE7A8 (~300 KB). Pointers inside scripts (FF06/FF09/FF0B-style)
  are not counted yet.
- **Menu strings** (file menu etc.): zero-terminated, bank C1, 0x1C285-0x1D3A1; read by `C1:8F16` from a pointer in
  `[$40]` (e.g. `$C8:F47C` -> `$C1:CD4C`). Table form not mapped yet.
- Other kana-dense regions found by `work/re/scan.py` (kana triples), owner unknown: 0x0CD7B-0x0D141,
  0x104C0-0x1143D, 0x41381-0x418D5, 0x46CF6-0x4756C, 0x5E8AA-0x5EFF5, 0x6E27A-0x6E61D, 0x8DFDE-0x8E9A2,
  0xBF8D6-0xBFEA0, 0xEE54C-0xEFD20, 0x1AE03F-0x1AFDB6, 0x21E958-0x21F706, 0x2200E8-0x2204A6, 0x221676-0x221B92,
  0x224C3E-0x225302, 0x240ED8-0x2415F6, 0x250AB0-0x251702, 0x270008-0x27057C (items, units, spells, battle and
  status text are the likely owners). Some (0x18Cxxx, 0x160Bxx, 0x1D0Bxx) are repeating patterns: probably tile maps.
