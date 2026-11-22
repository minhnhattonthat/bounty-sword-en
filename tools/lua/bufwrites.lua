-- Per-frame summary of writes to the window tile buffer halves ($7E:A000 + $1400 / $2400, 4 KB each):
-- one line per frame and writer (PC bank:page): count, lowest and highest address, plus $3729 (engine A cell cursor),
-- $374F (half select), $4D7B (C6 printer cursor). Card/dialogue overlap work (docs/status.md phase 8 to-do 8).
--   emu.py ... --script tools/debug/warp.lua --script tools/lua/bufwrites.lua --var FROM=2300
local from = FROM or 0
local agg = {}
local function hit(addr)
  if L.frame < from then return end
  local pc = L.pc()
  local key = string.format("%06X", pc & 0xFFFF00)
  local a = agg[key]
  if not a then a = {n = 0, lo = addr, hi = addr}; agg[key] = a end
  a.n = a.n + 1
  if addr < a.lo then a.lo = addr end
  if addr > a.hi then a.hi = addr end
end
L.on_write(0x7EB400, 0x7ED3FF, hit)
L.on_frame(function()
  if next(agg) == nil then return end
  local rd = function(a) return emu.read(a, emu.memType.snesMemory) end
  local cur = rd(0x7E3729) + 256 * rd(0x7E372A)
  local half = rd(0x7E374F)
  local c6 = rd(0x7E4D7B) + 256 * rd(0x7E4D7C)
  for k, a in pairs(agg) do
    L.log(string.format("f%d pc=%s n=%d lo=%06X hi=%06X 3729=%04X 374F=%02X 4D7B=%04X", L.frame, k, a.n, a.lo, a.hi,
      cur, half, c6))
  end
  agg = {}
end)
