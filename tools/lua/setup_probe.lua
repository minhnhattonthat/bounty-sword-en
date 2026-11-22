-- setup_probe.lua: log which battle-setup record (C4:2A39 table, parser C0:A3AE) a scene loads and every name
-- override it copies (C0:A542 loop start), with the unit slot. Use beside tools/debug/warp.lua:
--   emu.py ROM --out DIR --script tools/debug/warp.lua --script tools/lua/setup_probe.lua --var "SCENE='battle_status'"
-- Log lines: "SETUP idx=<n> f<frame>" (X / 3 at C0:A3B0), "SETUPNAME off=<file offset> slot=<n> f<frame>".
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function on_setup()
  local s = emu.getState()
  L.log(string.format("SETUP idx=%d f%d", s["cpu.x"] // 3, L.frame))
end
local function on_name()
  local s = emu.getState()
  local ptr = rd(0x30) | (rd(0x31) << 8) | (rd(0x32) << 16)
  local off = (ptr + s["cpu.y"]) & 0x3FFFFF
  L.log(string.format("SETUPNAME off=%06X slot=%d f%d", off, rd(0x24), L.frame))
end
-- COPYNAME="<file offset>" COPYSLOT=<n> (debug proof only): every frame, put that 12-byte override field from the
-- ROM into unit slot n's name buffer $7E1132+12n (default 4 = the hero on scenario 37's battle_status), so the
-- hero's status draws it. On every battle-status name copy (C2:5525, X = 12*slot) logs "SETUPBUF slot=<n> <hex>".
if COPYNAME then
  local off, base = tonumber(COPYNAME, 16), 0x7E1132 + 12 * (tonumber(COPYSLOT) or 4)
  emu.addEventCallback(L.safe(function()
    for k = 0, 11 do emu.write(base + k, rd(0xC00000 + off + k), emu.memType.snesMemory) end
  end), emu.eventType.endFrame)
end
local function on_status()
  local x = emu.getState()["cpu.x"]
  local hex = {}
  for k = 0, 11 do hex[#hex + 1] = string.format("%02X", rd(0x7E1132 + x + k)) end
  L.log(string.format("SETUPBUF slot=%d %s f%d", x // 12, table.concat(hex), L.frame))
end
emu.addMemoryCallback(L.safe(on_setup), emu.callbackType.exec, 0xC0A3B0, 0xC0A3B0, emu.cpuType.snes, emu.memType.snesMemory)
-- FIND="<hex bytes>" FINDF=<frame>: at that frame, log every WRAM address holding those bytes ("FOUND <addr>").
if FIND then
  local pat = {}
  for h in string.gmatch(FIND, "%x%x") do pat[#pat + 1] = tonumber(h, 16) end
  local done = false
  emu.addEventCallback(L.safe(function()
    if done or L.frame < (FINDF or 2400) then return end
    done = true
    for a = 0, 0x1FFFF - #pat do
      local ok = true
      for k = 1, #pat do
        if emu.read(a + k - 1, emu.memType.snesWorkRam) ~= pat[k] then ok = false; break end
      end
      if ok then L.log(string.format("FOUND %06X f%d", 0x7E0000 + a, L.frame)) end
    end
  end), emu.eventType.endFrame)
end
emu.addMemoryCallback(L.safe(on_status), emu.callbackType.exec, 0xC25525, 0xC25525, emu.cpuType.snes, emu.memType.snesMemory)
emu.addMemoryCallback(L.safe(on_name), emu.callbackType.exec, 0xC0A533, 0xC0A533, emu.cpuType.snes, emu.memType.snesMemory)
