-- rom_read_probe.lua: log the first read of each ROM byte in a range (CPU address), between two frames.
--   emu.py ROM --state-in X.mss --script tools/lua/rom_read_probe.lua --var RLO=0xC1C800 --var RHI=0xC1CB00
--     [--var FROM=600 --var TO=700]
-- Log lines: "READ <addr> f<frame>" in read order: which strings a screen builds from (results title, session ag).
local seen = {}
L.on_read(RLO or 0xC1C800, RHI or 0xC1CB00, function(a)
  if L.frame >= (FROM or 0) and L.frame <= (TO or 1e9) and not seen[a] then
    seen[a] = true
    L.log(string.format("READ %06X f%d", a, L.frame))
  end
end)
