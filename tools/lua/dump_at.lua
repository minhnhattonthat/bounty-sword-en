-- dump_at.lua: dump VRAM/CGRAM/OAM/PPU registers (L.dump_ppu) at one frame.
--   emu.py ROM --state-in X.mss --script tools/lua/dump_at.lua --var DUMP_AT=760 [--var "DUMP_NAME='ppu'"]
-- Writes <out>/<DUMP_NAME>.vram.bin etc. for vramfind.py / tilemap reads (results window title, session ag).
L.on_frame(function(f)
  if f == (DUMP_AT or 60) then
    L.dump_ppu(DUMP_NAME or "ppu")
    L.log("DUMPED f" .. f)
  end
end)
