-- Log the CPU's PC (K:PC) once every PC_EVERY frames from PC_FROM on, to find where a game hangs.
--   emu.py ... --script tools/debug/warp.lua --var KEEP=1 --script tools/lua/pclog.lua --var PC_FROM=2200
-- Also counts executions of the main-loop joypad read when JOY is set (24-bit address).
local from, every = PC_FROM or 0, PC_EVERY or 30
L.on_frame(function(f)
  if f < from or (f - from) % every ~= 0 then return end
  local s = emu.getState()
  L.log(string.format("PC f%d %02X:%04X A=%04X X=%04X Y=%04X D=%04X", f, s["cpu.k"] or 0, s["cpu.pc"] or 0,
    s["cpu.a"] or 0, s["cpu.x"] or 0, s["cpu.y"] or 0, s["cpu.d"] or 0))
end)
