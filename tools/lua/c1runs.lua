-- C1 string runs (asm/vwf.asm C1Run34/C1Run40): log each call's frame, scanline, start slot, word count and the
-- source pointer, so a garbled menu can be traced to its run and to NMI timing (scanline >= 225 = vblank).
--   emu.py BUILD --script tools/debug/warp.lua --var "SCENE='camp_items'" --script tools/lua/c1runs.lua
--          --var C1RUN34=0xFF03DA --var C1RUN40=0xFF03E5   (addresses: the JML targets at C1:8E90 / C1:8F13)
local n = 0
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function rd16(a) return rd(a) | (rd(a + 1) << 8) end
local function hit(tag)
  return function()
    n = n + 1
    if n > 400 then return end
    local st = emu.getState()
    local sl = st["ppu.scanline"] or -1
    local slot, cnt = rd16(0x2E), 0
    local ptr
    if tag == "34" then
      cnt = rd16(0x2C) >> 1
      ptr = rd16(0x34) | (rd(0x36) << 16)
    else
      ptr = rd16(0x40) | (rd(0x42) << 16)
      cnt = rd16(ptr)
    end
    L.log(string.format("f%d sl%d run%s slot=%04X n=%d ptr=%06X", L.frame, sl, tag, slot, cnt, ptr))
  end
end
L.on_exec(C1RUN34, C1RUN34, hit("34"))
L.on_exec(C1RUN40, C1RUN40, hit("40"))
