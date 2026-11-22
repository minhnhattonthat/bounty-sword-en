-- Master-message coverage runner (Mesen, via emu.py --script; driven by tools/debug/msgcover.py).
-- Loads HOOK_STATE (warp.lua msg scene, saved where the game has just copied a dialogue pointer to $7E3723) once
-- per master slot, swaps in that slot's pointer from the built table at $E6:D5EF, runs WAIT frames and logs
--   "TEXT <addr> f<frame>"        when the game read the message's first byte (textcover.py reads these lines)
--   "SLOT <n> <addr> ok|miss"     per slot; a slot whose pointer an earlier slot already showed is skipped
--   "MSGCOVER_DONE f<frame>"      at the end, then the run stops.
-- Globals: HOOK_STATE (path), FIRST/LAST (slot range, default 0..2461), WAIT (frames per message, default 60),
--          MSGSHOT (1: screenshot msg<slot>.png at the end of each wait: the first box of every message).
local M = emu.memType.snesMemory
local function rd(a) return emu.read(a, M) end
local MSG_PTR, MSG_TABLE = 0x7E3723, 0xE6D5EF
local first, last, wait = FIRST or 0, LAST or 2461, WAIT or 60

local slot, target, startAt, hit = first - 1, nil, nil, false
local done = {}

local function on_text_read(addr)
  if target and addr == target and not hit then
    hit = true
    L.log(string.format("TEXT %06X f%d", addr, L.frame))
  end
end
-- master text: banks $DE-$EA (in place) and $F0-$FE (spill); reads come through the $C0-$FF HiROM mirror
L.on_read(0xDE0000, 0xEAFFFF, on_text_read)
L.on_read(0xF00000, 0xFEFFFF, on_text_read)

local loading = false
local function next_slot()
  while true do
    slot = slot + 1
    if slot > last then
      L.log(string.format("MSGCOVER_DONE f%d", L.frame))
      L.finish(0)
      return
    end
    local p = MSG_TABLE + slot * 3
    local ptr = rd(p) | (rd(p + 1) << 8) | (rd(p + 2) << 16)
    if ptr ~= 0 and not done[ptr] then
      done[ptr] = true
      target, hit, startAt, loading = ptr, false, nil, true
      L.load_state(HOOK_STATE, function()
        emu.write(MSG_PTR, ptr & 0xFF, M); emu.write(MSG_PTR + 1, (ptr >> 8) & 0xFF, M)
        emu.write(MSG_PTR + 2, ptr >> 16, M)
        startAt, loading = L.frame, false
      end)
      return
    end
  end
end

assert(HOOK_STATE, "give --var \"HOOK_STATE=[[<path>]]\"")
L.on_frame(function(f)
  if loading then return end
  if not startAt then next_slot(); return end
  if f - startAt >= wait then
    if MSGSHOT == 1 then L.shot(string.format("msg%04d.png", slot)) end
    L.log(string.format("SLOT %d %06X %s", slot, target, hit and "ok" or "miss"))
    startAt = nil
    next_slot()
  end
end)
