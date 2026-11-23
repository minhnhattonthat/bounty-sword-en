; Location label (world map, chapter card) widened from 10 to 14 cells (decision D20), so full names fit:
; "Blackburn Mountains", "South Atlas Mountains" (112 px).
;
; C0:CB1E..CB6F drew it: BG2 scroll $0115/$011D (frame at x=136), frame tilemap from descriptor C0:CBE5
; (C0:2A79: src24 dst24 w h src-stride; 14x4 = 2 border + 10 text cells + 2 border), then 10 calls of C0:E1B1
; (one 8x16 cell each, words from C0:CD7B + (map-1)*20, buffer offset $22 += $20). Text cells are BG2 tiles
; $10+n (top) and $20+n (bottom); $1A-$1F / $2A-$2F were already the blank interior, so cells 10-13 land on them.
; Now: frame 18 wide (144 px) at x=104 (same right edge), 14 cells from LocWide = build/loc_wide.bin
; (build.py: 14 tag words per location, index map-1, tools/tag_font.py WIDE_CELLS). The 10-word table keeps the JP.
hirom

org $C0CB1E
    jml LocLabel

org $FFF000
LocLabel:
    lda.w #$FF98            ; was $FF78: 32 px further left
    sta.w $0115
    lda.w #$FFF8
    sta.w $011D
    sep #$20
    lda.b #LocDesc
    sta.b $48
    lda.b #LocDesc>>8
    sta.b $49
    lda.b #LocDesc>>16
    sta.b $4A
    rep #$20
    jsl $C02A79             ; frame tilemap -> $7F:0000
    lda.l $7FFD36
    dec
    asl
    asl
    sta.b $2E               ; (map-1)*4
    asl
    asl
    asl
    sec
    sbc.b $2E               ; (map-1)*28: 14 words a row
    tax
    lda.w #$0000
    sta.b $22
    lda.w #14
.cell:
    pha
    phx
    lda.l LocWide,x
    sta.b $20
    jsl $C0E1B1
    lda.b $22
    clc
    adc.w #$0020
    sta.b $22
    plx
    pla
    inx
    inx
    dec
    bne .cell
    jml $C0CB70

LocDesc:
    dl LocMap, $7F0000
    dw 18, 4, 36

LocMap:
    dw $3801, $3802, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $3803, $7802, $7801
    dw $3804, $3805, $3810, $3811, $3812, $3813, $3814, $3815, $3816, $3817, $3818, $3819, $381A, $381B, $381C, $381D, $7805, $7804
    dw $3806, $3807, $3820, $3821, $3822, $3823, $3824, $3825, $3826, $3827, $3828, $3829, $382A, $382B, $382C, $382D, $7807, $7806
    dw $3808, $3809, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $380A, $7809, $7808

LocWide:
    incbin "../build/loc_wide.bin"
assert pc() <= $FFFFFF
