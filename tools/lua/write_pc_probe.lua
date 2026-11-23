-- write_pc_probe.lua: log who writes a RAM range (CPU address), with the value and the writing code's address.
--   emu.py ROM --script ... --script tools/lua/write_pc_probe.lua --var WLO=0x7F0086 --var WHI=0x7F0090 [--var MAXLOG=200]
-- Log lines: "WRITE <addr>=<value> pc <K:PC> f<frame>": finds the code that builds a tilemap buffer (menu slices).
local n = 0
L.on_write(WLO or 0x7F0000, WHI or 0x7F0010, function(a, v)
  if n >= (MAXLOG or 200) then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("WRITE %06X=%02X pc %02X:%04X f%d", a, v, s["cpu.k"] or 0, s["cpu.pc"] or 0, L.frame))
end)
