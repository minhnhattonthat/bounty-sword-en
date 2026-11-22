# ROM layout, free space, graphics loading

## Header (verified)

- Title `ﾊﾞｳﾝﾃｨｿｰﾄﾞ1` (half-width kana), map mode `$31` (HiROM + FastROM), chip `$02` (ROM+RAM+battery),
  size byte `$0C`, SRAM `$03` (8 KB), file 3 MB (0x300000) with no copier header. Checksum/complement at
  `$FFDC` = `7a8a8575`.
- 3 MB HiROM: banks `$C0-$EF` (file 0x000000-0x2FFFFF). Expanding the file to 4 MB adds banks `$F0-$FF`
  (1 MB) for relocated text and code; keep size byte `$0C`; fix the checksum only in the release step.

## Free-space candidates (not yet trap-tested)

Runs of 1 KB+ of one byte value (`0x00` or `0xFF`), 50 KB in all. Candidates only: fill with a trap byte and tour before use.

| File range | Bytes | Fill |
|---|---|---|
| 0x07F267-0x080000 | 3481 | FF |
| 0x0F8B16-0x0FAC56 | 8512 | FF |
| 0x0FFB16-0x100000 | 1258 | FF |
| 0x189CAA-0x18A8AA | 3072 | 00 |
| 0x1A0B5C-0x1A1803 | 3239 | 00 |
| 0x1DAEE8-0x1DB912 | 2602 | 00 |
| 0x21FA98-0x220000 | 1384 | FF |
| 0x29E825-0x29F038 | 2067 | 00 |
| 0x2BF9AE-0x2C0000 | 1618 | FF |
| 0x2CF233-0x2D0000 | 3533 | FF |
| 0x2EF698-0x2F0000 | 2408 | FF |
| 0x2FD8CB-0x300000 | 10037 | FF |

Smaller 00 runs at 0x11CC04, 0x12F770, 0x2B0B10, 0x2B1386, 0x2B1B5E (1-1.7 KB, inside data banks: likely tables).
Plan: put the English script in the expanded 1 MB, not in these.

## Compression and graphics loading (partly verified)

- No text compression (text is raw 16-bit words).
- Graphics reach VRAM only from WRAM: every VRAM DMA in the intro and first scenes is from `$7E:A000-$7E:C7FF`
  (staging) or `$7F:0000` (text-window tilemap), by the NMI DMA routine at `C0:989C` (`snes_dmalog.lua`, run from
  `work/qa/orig_g1/s002000.mss`).
- The staging loader `C0:9A30` copies words straight from ROM (`[$74]`, e.g. bank `$E6`) into `$7E:A000`, unless bit
  `$20` of `$7E:2024` is set, then `C0:9AB2` expands the data (length/16: per-tile, likely a bitplane expansion,
  not LZ: guess, unread). So `vramfind.py` against the raw ROM should find most tiles; expanded blocks need that routine.
- No general LZ decompressor found yet; watch writes to the WRAM target when a screen's tiles are not found raw.
