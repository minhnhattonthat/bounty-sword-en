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

; ---- menus, engine B, name tags through the C1 glyph-address routine: English codes read the English font ----
org $C186A9
    jml C1Glyph

; ---- dialogue (engine A) glyph draw, JSR'd from C2:47DA with the code in $2E: proportional ----
org $C24922
    jml VwfDraw

; ---- speaker name tag (FF0E path, C2:55C6..): Y = glyph offset computed the game's way, base pointer set here ----
org $C25641
    jml NameGlyph

; The English font sits where the game's 16-bit glyph-offset formula puts codes $0F20-$0F7F when the base is
; $FF:0000 (tools/font_en.py font_block): offset(c) = ((c & $FFF0) << 5) + ((c & $F) << 4), truncated to 16 bits.
org $FFE400
EnFont:
    incbin "../build/font_en.bin"
assert pc() == $FFF000

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

; Replaces C2:5641-C2:5650 (set $44/$46 = $EB:2D8C). Y = glyph offset; English codes give Y >= $E400 (JP codes
; stay below $A000), and read the English font with base $FF:0000.
NameGlyph:
    cpy.w #$E400
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
    lda.l $7E3729
    cmp.w !LAST
    beq .same
    lsr
    sta.w !BASE
    stz.w !PX
.same:
    lda.w !PX
    and.w #$0007
    sta.w !S
    lda.w #$1400
    sta.w !T
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
    clc
    adc.w #$0007
    lsr
    lsr
    lsr
    clc
    adc.w !BASE
    asl
    sta.l $7E3729
    sta.w !LAST
    lda.l $7E3727
    inc
    inc
    sta.l $7E3727
    plb
    plp
    jml $C249CD         ; the RTS that ended the original routine

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

assert pc() <= $FF8000
