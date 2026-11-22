-- regionreads.lua: log the first read of each ROM byte inside the given file-offset ranges, with the reading PC.
-- Confirms which code reads a text table (docs/re/text.md §Text inventory) while tools/debug/warp_all.py tours scenes:
--   warp_all.py --script tools/lua/regionreads.lua --var "RANGES='00CD7B-00D151,0BF8AE-0C0004'"
-- HiROM: file offset X is mapped at bank $C0|X>>16 (and $40|.., and $00/$80|.. when X & 0xFFFF >= 0x8000).
-- Log lines: "RR <fileoff> pc=<PC>".
local seen = {}
local function hook(addr, value)
  local off = addr & 0x3FFFFF
  if seen[off] then return end
  seen[off] = true
  local s = emu.getState()
  L.log(string.format("RR %06X pc=%02X%04X f%d", off, s["cpu.k"], s["cpu.pc"], L.frame))
end
local function add(lo, hi)  -- CPU range within one bank
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, lo, hi, emu.cpuType.snes, emu.memType.snesMemory)
end
for slo, shi in string.gmatch(RANGES, "(%x+)-(%x+)") do
  local lo, hi = tonumber(slo, 16), tonumber(shi, 16) - 1
  local b = lo >> 16
  while b <= (hi >> 16) do
    local a0 = math.max(lo, b << 16) & 0xFFFF
    local a1 = math.min(hi, (b << 16) | 0xFFFF) & 0xFFFF
    add(((0xC0 | b) << 16) | a0, ((0xC0 | b) << 16) | a1)
    if b < 0x3E then add(((0x40 | b) << 16) | a0, ((0x40 | b) << 16) | a1) end
    if a1 >= 0x8000 then
      local c0 = math.max(a0, 0x8000)
      add((b << 16) | c0, (b << 16) | a1)
      add(((0x80 | b) << 16) | c0, ((0x80 | b) << 16) | a1)
    end
    b = b + 1
  end
end
