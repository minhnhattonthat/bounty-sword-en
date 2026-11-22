-- Which WRAM bytes in a range are ever written? Logs the never-written runs every 600 frames (the last log wins).
--   emu.py ... --script tools/debug/warp.lua --script tools/lua/wramfree.lua --var LO=0x7F8000 --var HI=0x7FFFFF
-- Used to pick a home for the VWF state (docs/re/vwf.md).
local lo, hi = assert(LO, "set --var LO=0x..."), assert(HI, "set --var HI=0x...")
local hit = {}
-- Boot clears all of WRAM, so a byte only counts as used once something non-zero lands there after frame 200.
L.on_write(lo, hi, function(addr, value) if L.frame > 200 and value ~= 0 then hit[addr] = true end end)
L.on_frame(function()
  if L.frame % 600 ~= 0 then return end
  local runs, start = {}, nil
  for a = lo, hi + 1 do
    if a <= hi and not hit[a] then
      start = start or a
    elseif start then
      if a - start >= 32 then runs[#runs + 1] = string.format("%06X-%06X(%d)", start, a - 1, a - start) end
      start = nil
    end
  end
  L.log(string.format("f%d free: %s", L.frame, table.concat(runs, " ")))
end)
