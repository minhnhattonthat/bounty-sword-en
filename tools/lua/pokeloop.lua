-- Hold RAM bytes at fixed values every frame from POKE_FROM on (a candidate test: does the screen show the value?).
--   emu.py ... --script tools/lua/pokeloop.lua --var "HOLDPOKE='7FFCB0:D204,7E6A56:2E16'" --var POKE_FROM=1000
-- HOLDPOKE: comma list ADDR:HEX (hex bytes in memory order, e.g. D204 = 1234 as a little-endian u16).
local M = emu.memType.snesMemory
local list = {}
for addr, hex in (HOLDPOKE or ""):gmatch("(%x+):(%x+)") do
  local bytes = {}
  for i = 0, #hex / 2 - 1 do bytes[#bytes + 1] = tonumber(hex:sub(2 * i + 1, 2 * i + 2), 16) end
  list[#list + 1] = { tonumber(addr, 16), bytes }
end
local from = POKE_FROM or 0
L.on_frame(function(f)
  if f < from then return end
  for _, p in ipairs(list) do
    for i, b in ipairs(p[2]) do emu.write(p[1] + i - 1, b, M) end
  end
end)
