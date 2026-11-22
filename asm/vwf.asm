; vwf.asm: English font hooks (docs/re/vwf.md). build.py assembles it with asar onto build/bounty_en.sfc after the
; text step; build/font_en*.bin come from tools/font_en.py. English codes are $0F20-$0F7E (ASCII + $0F00).
hirom

!EN_BASE = $0F20
!EN_END = $0F7F

; VWF state, bank $7F (never written by the game in prologue, battle or camp: tools/lua/wramfree.lua)
!LAST = $FF80           ; the $3729 value this code wrote last; any other value means the engine moved the cursor
!BASE = $FF82           ; cell index where the current line run starts
!PX = $FF84             ; pixels drawn since BASE
!W = $FF86              ; advance of the glyph being drawn
!BOT = $FF88            ; offset of the glyph's bottom tile in its source (EN $10, JP font $100)
!D0 = $FF8A             ; buffer offset of the cell the glyph starts in
!D1 = $FF8C             ; buffer offset of the next cell
!S = $FF8E              ; px & 7
!ROW = $FF90
!M = $FF92              ; glyph mask, high byte = left cell part, low byte = right cell part
!P0 = $FF94             ; plane 0, same split
!P1 = $FF96             ; plane 1, same split
!SPILL = $FF98          ; nonzero when the glyph runs into the next cell
!T = $FF9A              ; scratch
!R = $FF9C              ; row offset inside the cell ($00-$0E top tile, $200-$20E bottom tile)
!LAST6 = $FF9E          ; LAST/BASE/PX of the C6 printer (narration, card subtitle), swapped in by SwapC6
!PXSTART = $FFA4        ; first PX of the next run (card subtitle centring), consumed by the run start
!MODE = $FFA6           ; 0 = engine A (C2:4922), 1 = C6 printer (C6:DF04), 2 = C1 string run (C1Run)
!C1N = $FFA8            ; C1 run: cells in the field (the string's word count)
!C1LO = $FFAA           ; start slot & $0F
!C1HI = $FFAC           ; start slot & $FFF0
!C1I = $FFAE            ; byte index of the next word
!C1LEN = $FFB0          ; field length in bytes
!C1PAIR = $FFB2         ; second letter of a packed pair still to draw (0 = none)

!TAB = $0F7F            ; C1 runs: move to the next cell boundary (blank glyph elsewhere)
!SETX = $0F1F           ; C1 runs: the next word is a cell number, PX = cell * 8 (tools/grid.py)

; ---- menus, engine B, name tags through the C1 glyph-address routine: English codes read the English font ----
org $C186A9
    jml C1Glyph

; ---- dialogue (engine A) glyph draw, JSR'd from C2:47DA with the code in $2E: proportional ----
org $C24922
    jml VwfDraw

; ---- speaker name tag (FF0E path, C2:55C6..): Y = glyph offset computed the game's way, base pointer set here ----
org $C25641
    jml NameGlyph

; ---- location label (world map, chapter card), C0:E1B1 one cell per call: $2E = glyph offset, base set here ----
org $C0E1CB
    jml CardGlyph

; ---- C6 printer (chapter-card subtitle, mode 14; narration, mode 15): glyph draw JSR'd from C6:DD8F/DE60 with the
; code in $20, same cell table and buffer as engine A: the same VWF ----
org $C6DF04
    jml C6Vwf

; ---- chapter-card subtitle centring (was: start cell from table C6:D421 by line-1 length, lengths 0-19 only):
; centre line 1 by its pixel width ----
org $C6D383
    jml CardCentre

; ---- C1 string runs (menus, lists, windows): C1:8E90 draws $2C/2 words from [$34] at tile slot $2E (19 callers),
; C1:8F13 draws a [count][words] string from [$40]. Runs holding English go through the VWF core (mode 2): the
; field keeps its slots, text is packed by pixels, and a word $2020-$7E7E holds two ASCII letters ----
org $C18E90
    jml C1Run34
org $C18F13
    jml C1Run40

; The English font sits where the game's 16-bit glyph-offset formula puts codes $0F20-$0F7F when the base is
; $FF:0000 (tools/font_en.py font_block): offset(c) = ((c & $FFF0) << 5) + ((c & $F) << 4), truncated to 16 bits.
org $FFE400
EnFont:
    incbin "../build/font_en.bin"
assert pc() == $FFF000

; Speaker tags and location labels pre-rendered by the build (tools/tag_font.py): codes $0500-$0F1E, offsets
; $A000-$E3EF with base $FF:0000.
org $FFA000
TagFont:
    incbin "../build/font_tag.bin"
assert pc() <= $FFE400

org $FF0000
EnWidth:
    incbin "../build/font_en_w.bin"

; A (16-bit) = code -> A = the game's glyph offset for it. JSR from bank $FF code.
GlyphOffset:
    pha
    and.w #$FFF0
    asl
    asl
    asl
    asl
    asl
    pha
    lda 3,s
    and.w #$000F
    asl
    asl
    asl
    asl
    clc
    adc 1,s
    sta 3,s
    pla
    pla
    rts

; In: A (16-bit) = character code. Out: $48/$4A = top tile pointer, $44/$46 = bottom tile pointer, A kept.
C1Glyph:
    cmp.w #!EN_BASE
    bcc .orig
    cmp.w #!EN_END
    bcs .orig
    pha
    jsr GlyphOffset
    sta $48
    clc
    adc.w #$0100
    sta $44
    lda.w #$00FF
    sta $4A
    sta $46
    pla
    rtl
.orig:
    pha                 ; the four bytes the hook replaced
    lda.w #$00EB
    jml $C186AD

; Replaces C2:5641-C2:5650 (set $44/$46 = $EB:2D8C). Y = glyph offset; English and tag codes give Y >= $A000 (JP
; codes stay below $A000), and read the English font / tag tiles with base $FF:0000.
NameGlyph:
    cpy.w #$A000
    bcc .jp
    stz $44
    sep #$20
    lda.b #$FF
    sta $46
    rep #$20
    jml $C25651
.jp:
    sep #$20
    lda.b #$8C
    sta $44
    lda.b #$2D
    sta $45
    lda.b #$EB
    sta $46
    rep #$20
    jml $C25651

; Replace SEP #$20 / $44-$46 = $EB:2D8C (8-bit stores) / REP #$20, 16 bytes ending at RET. $2E = glyph offset,
; English and tag codes >= $A000. Used by C0:E1CB (location label).
macro FontBase2E(ret)
    lda $2E
    cmp.w #$A000
    bcc ?jp
    stz $44
    sep #$20
    lda.b #$FF
    sta $46
    jml <ret>
?jp:
    sep #$20
    lda.b #$8C
    sta $44
    lda.b #$2D
    sta $45
    lda.b #$EB
    sta $46
    jml <ret>
endmacro

; Replaces C6:D383-C6:D38A (LDA $2E / ASL / TAX / LDA $C6D421,x -> A = start cell x2, stored to $7E4D7B).
; [$48] = the subtitle, $7E4D79 its start; line 1 ends at the first word >= $8000 (FFFF, names) as in the
; original count. Width as VwfDraw draws it: English from EnWidth, 「」 as '"', anything else 8 px.
CardCentre:
    lda.l $7E4D79
    tay
    stz $2C
.sum:
    lda [$48],y
    bmi .done
    cmp.w #$0036
    beq .quote
    cmp.w #$0037
    bne +
.quote:
    lda.w #!EN_BASE+2
+
    cmp.w #!EN_BASE
    bcc .jp
    cmp.w #!EN_END
    bcs .jp
    sec
    sbc.w #!EN_BASE
    tax
    lda.l EnWidth,x
    and.w #$00FF
    bra .add
.jp:
    lda.w #$0008
.add:
    clc
    adc $2C
    sta $2C
    iny
    iny
    bra .sum
.done:
    lda.w #160
    sec
    sbc $2C
    bpl +
    lda.w #$0000
+
    lsr
    sta.l $7F0000+!PXSTART
    lda.w #$FFFF        ; force a new run at cell 0
    sta.l $7F0000+!LAST6
    lda.w #$0000
    jml $C6D38B

CardGlyph:
    %FontBase2E($C0E1D9)

; Replaces C6:DF04 (PHX / LDA $20 ...); returns through C6:DF96 (PLX / RTS), so the original's INC of $7E4D7B is
; skipped: VwfDraw sets it.
C6Vwf:
    phx
    php
    phb
    rep #$30
    pea $7F7F
    plb
    plb
    lda $20
    sta $2E
    lda.w #$0001
    sta.w !MODE
    jsr SwapC6
    jmp VwfCommon

; Swap LAST/BASE/PX with the C6 printer's copies (DB = $7F, 16-bit).
SwapC6:
    ldx.w #$0004
-
    lda.w !LAST,x
    pha
    lda.w !LAST6,x
    sta.w !LAST,x
    pla
    sta.w !LAST6,x
    dex
    dex
    bpl -
    rts

; Replaces C2:4922-C2:49CD. Draws the glyph for code $2E at pixel position PX of the current line run into the
; window tile buffer ($7E:A000 + $1400/$2400, cell offsets from the table at C2:49CE), then advances $3727 (script)
; and $3729 (cell cursor, rounded up to the next empty cell so the engine's line logic still works).
VwfDraw:
    php
    phb
    rep #$30
    pea $7F7F
    plb
    plb
    stz.w !MODE
VwfCommon:
    lda.w #$0100        ; both fonts keep a glyph's bottom tile $100 after its top tile
    sta.w !BOT
    lda $2E
    cmp.w #$0036        ; 「 and 」 stay in the script (C2:48B3 ends a speech on 」 FFFF) but draw as '"'
    beq .quote
    cmp.w #$0037
    bne +
.quote:
    lda.w #!EN_BASE+2
+
    pha
    jsr GlyphOffset
    sta $44
    pla
    cmp.w #!EN_BASE
    bcc .jp
    cmp.w #!EN_END
    bcs .jp
    sec                 ; English: advance from the width table, font in bank $FF
    sbc.w #!EN_BASE
    tax
    lda.l EnWidth,x
    and.w #$00FF
    sta.w !W
    sep #$20
    lda.b #$FF
    sta $46
    rep #$20
    bra .pos
.jp:
    lda $44             ; Japanese: the game's font at $EB:2D8C, one full cell
    clc
    adc.w #$2D8C
    sta $44
    sep #$20
    lda.b #$EB
    sta $46
    rep #$20
    lda.w #$0008
    sta.w !W
.pos:
    lda.w !MODE
    cmp.w #$0002
    bne +
    jmp .c1pos
+
    lda.w !MODE
    bne +
    lda.l $7E3729
    bra ++
+
    lda.l $7E4D7B
++
    cmp.w !LAST
    beq .same
    lsr
    sta.w !BASE
    lda.w !PXSTART
    sta.w !PX
    stz.w !PXSTART
.same:
    lda.w !PX
    and.w #$0007
    sta.w !S
    lda.w #$1400
    sta.w !T
    lda.w !MODE         ; the C6 printer has one buffer half
    bne +
    lda.l $7E374F
    beq +
    lda.w #$2400
    sta.w !T
+
    lda.w !PX
    lsr
    lsr
    lsr
    clc
    adc.w !BASE
    asl
    tax
    lda.l $C249CE,x
    clc
    adc.w !T
    sta.w !D0
    lda.l $C249D0,x
    clc
    adc.w !T
    sta.w !D1
    stz.w !SPILL
    lda.w !S
    clc
    adc.w !W
    cmp.w #$0009
    bcc +
    inc.w !SPILL
    ldx.w !D1
    jsr ClearCell
+
    lda.w !S
    bne +
    ldx.w !D0
    jsr ClearCell
+
.rows:
    stz.w !ROW
.row:
    lda.w !ROW
    cmp.w #$0008
    bcs .bottom
    asl
    sta.w !R
    tay
    bra .src
.bottom:
    sec
    sbc.w #$0008
    asl
    pha
    clc
    adc.w #$0200
    sta.w !R
    pla
    clc
    adc.w !BOT
    tay
.src:
    lda [$44],y         ; low byte plane 0, high byte plane 1
    sta.w !T
    sep #$20
    lda.w !T+1
    eor.b #$FF
    ora.w !T            ; mask: every pixel that isn't background (colour 2 = plane0 0, plane1 1)
    sta.w !M+1
    stz.w !M
    lda.w !T+1
    and.w !M+1
    sta.w !P1+1
    stz.w !P1
    lda.w !T
    sta.w !P0+1
    stz.w !P0
    rep #$20
    ldx.w !S
    beq .shifted
-
    lsr.w !M
    lsr.w !P0
    lsr.w !P1
    dex
    bne -
.shifted:
    lda.w !D0
    clc
    adc.w !R
    tax
    sep #$20
    lda.w !M+1
    eor.b #$FF
    and.l $7EA000,x
    ora.w !P0+1
    sta.l $7EA000,x
    lda.w !M+1
    eor.b #$FF
    and.l $7EA001,x
    ora.w !P1+1
    sta.l $7EA001,x
    rep #$20
    lda.w !SPILL
    beq .next
    lda.w !D1
    clc
    adc.w !R
    tax
    sep #$20
    lda.w !M
    eor.b #$FF
    and.l $7EA000,x
    ora.w !P0
    sta.l $7EA000,x
    lda.w !M
    eor.b #$FF
    and.l $7EA001,x
    ora.w !P1
    sta.l $7EA001,x
    rep #$20
.next:
    inc.w !ROW
    lda.w !ROW
    cmp.w #$0010
    bcs +
    jmp .row
+
    lda.w !PX
    clc
    adc.w !W
    sta.w !PX
    ldx.w !MODE
    cpx.w #$0002
    bne +
    plb                 ; mode 2: back to C1Run (JSR'd through C1Glyph1)
    plp
    rts
+
    clc
    adc.w #$0007
    lsr
    lsr
    lsr
    clc
    adc.w !BASE
    asl
    ldx.w !MODE
    beq .engA
    sta.l $7E4D7B
    sta.w !LAST
    jsr SwapC6
    plb
    plp
    jml $C6DF96         ; PLX / RTS of the original C6 routine
.engA:
    sta.l $7E3729
    sta.w !LAST
    lda.l $7E3727
    inc
    inc
    sta.l $7E3727
    plb
    plp
    jml $C249CD         ; the RTS that ended the original routine

; mode 2 (C1 run): cells are tile slots from the run's start slot; the field was cleared by C1Run, and a glyph never
; spills past the field's last cell.
.c1pos:
    lda.w !PX
    and.w #$0007
    sta.w !S
    stz.w !SPILL
    lda.w !PX
    lsr
    lsr
    lsr
    pha
    jsr C1SlotOff
    sta.w !D0
    pla
    inc
    cmp.w !C1N
    bcs +
    jsr C1SlotOff
    sta.w !D1
    lda.w !S
    clc
    adc.w !W
    cmp.w #$0009
    bcc +
    inc.w !SPILL
+
    jmp .rows

; X = buffer offset of a cell: fill both tiles with background (colour 14: planes 0/1 = 00/FF, planes 2/3 = FF/FF).
ClearCell:
    ldy.w #$0008
-
    lda.w #$FF00
    sta.l $7EA000,x
    sta.l $7EA200,x
    lda.w #$FFFF
    sta.l $7EA010,x
    sta.l $7EA210,x
    inx
    inx
    dey
    bne -
    rts

; ---- C1 string runs ----
; Replaces C1:8E90 (PHY / LDY #0 / per word: JSL C1:8EB9, slot $2E + 1, rows of 16 slots 2 apart / PLY / RTL).
C1Run34:
    phx
    phy
    lda $2C
    lsr
    jsr C1Run
    ply
    plx
    rtl

; Replaces C1:8F13 ([$40] = count word, then the words; $2E = start slot).
C1Run40:
    lda $34
    pha
    lda $36
    pha
    lda $40
    clc
    adc.w #$0002
    sta $34
    lda $42
    adc.w #$0000
    and.w #$00FF
    sta $36
    lda [$40]
    jsr C1Run
    pla
    sta $36
    pla
    sta $34
    rtl

; A = word count N, [$34] = words, $2E = start slot. Out: $2E = the slot after the field, as the original loop.
; All-Japanese runs take the original per-cell path, so the JP build and JP strings draw as before.
C1Run:
    php
    phb
    rep #$30
    pea $7F7F
    plb
    plb
    sta.w !C1N
    asl
    sta.w !C1LEN
    tay
-
    dey
    dey
    bpl +
    jmp .jp
+
    lda [$34],y
    jsr C1IsEn
    bcc -
    lda $2E
    and.w #$000F
    sta.w !C1LO
    lda $2E
    and.w #$FFF0
    sta.w !C1HI
    ldy.w #$0000
-
    cpy.w !C1N
    bcs +
    phy
    tya
    jsr C1SlotOff
    tax
    jsr ClearCell
    ply
    iny
    bra -
+
    stz.w !PX
    stz.w !C1I
    stz.w !C1PAIR
.loop:
    lda.w !C1PAIR
    beq +
    stz.w !C1PAIR
    bra .glyph
+
    ldy.w !C1I
    cpy.w !C1LEN
    bcs .done
    lda [$34],y
    iny
    iny
    sty.w !C1I
    cmp.w #!TAB
    bne +
    lda.w !PX           ; next cell after the ink: ceil((PX-1)/8)*8 (a glyph's last, blank column may spill;
    clc                 ; at a cell edge TAB stays; tools/grid.py skips a cell with a space first)
    adc.w #$0006
    and.w #$FFF8
    sta.w !PX
    bra .loop
+
    cmp.w #!SETX        ; SETX n: PX = n * 8 (jump to cell n; grid strings with long gaps)
    bne +
    lda [$34],y
    iny
    iny
    sty.w !C1I
    asl
    asl
    asl
    sta.w !PX
    bra .loop
+
    cmp.w #$2020        ; packed pair: high byte first, low byte next
    bcc .glyph
    cmp.w #$7F00
    bcs .glyph
    pha
    and.w #$00FF
    clc
    adc.w #$0F00
    sta.w !C1PAIR
    pla
    xba
    and.w #$00FF
    clc
    adc.w #$0F00
.glyph:
    pha
    lda.w !PX
    lsr
    lsr
    lsr
    cmp.w !C1N
    pla
    bcs .loop           ; past the field: dropped (the fit lint keeps text inside)
    sta $2E
    jsr C1Glyph1
    bra .loop
.done:
    lda.w !C1N
    jsr C1Slot
    sta $2E
    plb
    plp
    rts
.jp:
    ldy.w #$0000
-
    cpy.w !C1LEN
    bcs +
    lda [$34],y
    jsl $C18EB9
    lda $2E
    inc
    and.w #$000F
    bne ++
    lda $2E
    and.w #$00F0
    clc
    adc.w #$0020
    sta $2E
    bra +++
++
    inc $2E
+++
    iny
    iny
    bra -
+
    plb
    plp
    rts

; carry set if word A is English: $0F20-$0F7F, or a packed pair with both bytes $20-$7E
C1IsEn:
    cmp.w #!EN_BASE
    bcc .no
    cmp.w #!TAB+1
    bcc .yes
    cmp.w #$2020
    bcc .no
    cmp.w #$7F00
    bcs .no
    pha
    and.w #$00FF
    cmp.w #$0020
    bcc +
    cmp.w #$007F
    bcs +
    pla
    sec
    rts
+
    pla
.no:
    clc
    rts
.yes:
    sec
    rts

; A = cell k of the run -> A = its slot: (start & $FFF0) + (t >> 4) * $20 + (t & $F), t = (start & $F) + k
C1Slot:
    clc
    adc.w !C1LO
    pha
    and.w #$000F
    sta.w !T
    pla
    and.w #$FFF0
    asl
    clc
    adc.w !T
    clc
    adc.w !C1HI
    rts

; A = cell k -> A = its offset from $7E:A000 (32 bytes a slot; the bottom tile is +$200, 16 slots on)
C1SlotOff:
    jsr C1Slot
    asl
    asl
    asl
    asl
    asl
    rts

; $2E = code: draw it at PX through the VWF core (mode 2, DB = $7F, 16-bit)
C1Glyph1:
    php
    phb
    lda.w #$0002
    sta.w !MODE
    jmp VwfCommon

assert pc() <= $FF8000
