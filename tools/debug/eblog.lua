-- Log the main-loop continuation ($00EB-$00ED) whenever it changes: finds a screen's idle/input loop for warp gates.
--   emu.py ... --script tools/debug/warp.lua --var "SCENE='x'" --var KEEP=true --script tools/debug/eblog.lua
local M = emu.memType.snesMemory
local last
L.on_frame(function(f)
  local eb = emu.read(0xEB, M) | (emu.read(0xEC, M) << 8) | (emu.read(0xED, M) << 16)
  if eb ~= last then last = eb; L.log(string.format("EB %06X f%d", eb, f)) end
end)
