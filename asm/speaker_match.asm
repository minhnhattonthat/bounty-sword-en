; speaker_match.asm: battle-map speaker portraits with English unit names (applied after vwf.asm by build.py).
;
; FF15 on the battle map (C2:59B1) finds the speaker's portrait by comparing the 6-word speaker header with the
; names of the deployed units ($1132 + 12 * slot, C2:5C9B) and the party ($7FF4E3, C2:5CDA). The build writes the
; header as pre-rendered tag codes (tools/tag_font.py) but unit names as English letter codes
; (script/default_names.tsv, unit_names), so nothing matched: a boss without a speaker-table row kept the last
; portrait shown (Thetis for 盗賊のボス, user report 2026-11-23, rom/bounty_wrong_avatar.mss).
; Each compare now tries the original match, then the build's map (build/spk_map.bin, written by build.py:
; 24-byte rows = 6 header words, 6 unit-name words; ends with a $FFFF word): a header in the map also matches
; its unit name. Entry state as the original routines: A/X/Y 16-bit, Y = header offset in [$48], X = name
; offset; result in Z, returned through the routine's own RTS (JML keeps the flags). A, X, Y are scratch: the
; caller reloads Y from $7E3727 and X from its loop counter. No RAM is used besides the stack.
hirom

org $C25C9B
    jml SpkUnit         ; was LDA [$48],y / CMP $1132,x ... (RTS at C2:5CD9)
org $C25CDA
    jml SpkParty        ; was LDA [$48],y / CMP $7FF4E3,x ... (RTS at C2:5D1E)

; 6-word compare of [$48],y with <a>,x (abs or long); falls through with Z = equal; X and Y advance.
macro cmp6(a)
    lda [$48],y
    cmp <a>,x
    bne ?out
    iny
    iny
    inx
    inx
    lda [$48],y
    cmp <a>,x
    bne ?out
    iny
    iny
    inx
    inx
    lda [$48],y
    cmp <a>,x
    bne ?out
    iny
    iny
    inx
    inx
    lda [$48],y
    cmp <a>,x
    bne ?out
    iny
    iny
    inx
    inx
    lda [$48],y
    cmp <a>,x
    bne ?out
    iny
    iny
    inx
    inx
    lda [$48],y
    cmp <a>,x
?out:
endmacro

; The routine body: <a> = the name array (abs or long), <ret> = the original routine's RTS.
; Stack: phx, phy; on a mapped header the 6 value words go on top (1..11,s), Y at 13,s, X at 15,s.
macro speaker(a, ret)
    phx
    phy
    %cmp6(<a>)
    beq ?yes
    ply
    phy
    jsr MapFind         ; C = found, X = row
    bcc ?no
    lda.l SpkMap+22,x
    pha
    lda.l SpkMap+20,x
    pha
    lda.l SpkMap+18,x
    pha
    lda.l SpkMap+16,x
    pha
    lda.l SpkMap+14,x
    pha
    lda.l SpkMap+12,x
    pha
    lda 15,s            ; X at entry
    tax
    lda 1,s
    cmp <a>,x
    bne ?neq
    lda 3,s
    cmp <a>+2,x
    bne ?neq
    lda 5,s
    cmp <a>+4,x
    bne ?neq
    lda 7,s
    cmp <a>+6,x
    bne ?neq
    lda 9,s
    cmp <a>+8,x
    bne ?neq
    lda 11,s
    cmp <a>+10,x
    bne ?neq
    ldx.w #$0000
    bra ?clean
?neq:
    ldx.w #$0001
?clean:
    tsc                 ; drop the 6 words, Y and X
    clc
    adc.w #16
    tcs
    cpx.w #$0000        ; Z = matched
    jml <ret>
?yes:
    ply
    plx
    lda.w #$0000        ; Z = 1
    jml <ret>
?no:
    ply
    plx
    lda.w #$0001        ; Z = 0
    jml <ret>
endmacro

org $FF8000
SpkUnit:
    %speaker($1132, $C25CD9)
SpkParty:
    %speaker($7FF4E3, $C25D1E)

; Y = header offset in [$48]: C = 1 and X = row offset when the 6 header words are a key of SpkMap. Keeps Y.
MapFind:
    ldx.w #$0000
.row:
    lda.l SpkMap,x
    cmp.w #$FFFF
    beq .none
    phy
    lda.l SpkMap,x
    cmp [$48],y
    bne .next
    iny
    iny
    lda.l SpkMap+2,x
    cmp [$48],y
    bne .next
    iny
    iny
    lda.l SpkMap+4,x
    cmp [$48],y
    bne .next
    iny
    iny
    lda.l SpkMap+6,x
    cmp [$48],y
    bne .next
    iny
    iny
    lda.l SpkMap+8,x
    cmp [$48],y
    bne .next
    iny
    iny
    lda.l SpkMap+10,x
    cmp [$48],y
    bne .next
    ply
    sec
    rts
.next:
    ply
    txa
    clc
    adc.w #24
    tax
    bra .row
.none:
    clc
    rts

SpkMap:
    incbin "../build/spk_map.bin"
assert pc() <= $FFA000
