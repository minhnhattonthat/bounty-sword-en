-- vram_dma_probe.lua: log DMA transfers into a VRAM word range with their source, to trace where tiles come from.
--   emu.py ROM --state-in X.mss --script tools/lua/vram_dma_probe.lua --var VLO=0x1000 --var VHI=0x1180
-- Log lines: "DMA f<frame> ch<n> src <bank:addr> len <bytes> vram <word addr>". Tracks $2116/$2117 writes (the
-- VRAM address registers are write-only) and reads the channel registers when $420B starts a transfer.
local vaddr = 0
local lo, hi = VLO or 0x1000, VHI or 0x1180
L.on_write(0x2116, 0x2117, function(a, v)
  if a == 0x2116 then vaddr = (vaddr & 0xFF00) | v else vaddr = (vaddr & 0x00FF) | (v << 8) end
end)
L.on_write(0x420B, 0x420B, function(_, v)
  for ch = 0, 7 do
    if v & (1 << ch) ~= 0 then
      local b = 0x4300 + ch * 0x10
      local dest = emu.read(b + 1, emu.memType.snesMemory)
      if dest == 0x18 or dest == 0x19 then
        local src = emu.read(b + 2, emu.memType.snesMemory) | (emu.read(b + 3, emu.memType.snesMemory) << 8)
        local bank = emu.read(b + 4, emu.memType.snesMemory)
        local len = emu.read(b + 5, emu.memType.snesMemory) | (emu.read(b + 6, emu.memType.snesMemory) << 8)
        if len == 0 then len = 0x10000 end
        if vaddr < hi and vaddr + len // 2 > lo then
          L.log(string.format("DMA f%d ch%d src %02X:%04X len %d vram %04X", L.frame, ch, bank, src, len, vaddr))
        end
      end
    end
  end
end)
