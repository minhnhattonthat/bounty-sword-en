-- Side-table coverage runner (Mesen, via emu.py --state-in STATE --script; driven by tools/debug/sidecover.py).
-- Starts on a menu that draws a table's strings through a drawer whose source pointer sits in direct-page RAM
-- (the C1 string run C1:8E90 -> C1Run34 reads its pointer from $34-$36). Every call of HOOK whose pointer lies in
-- [LO, HI) gets the next TARGETS address instead, and KEYS (a route, "6 down;40 -") is pressed over and over to make
-- the menu redraw, until every target has been drawn or STALL rounds pass with no new one.
-- Logs "TEXT <addr> f<frame>" when the game reads a target's first byte (scripts/textcover.py), "SWAP <addr>" per
-- swap, a shot round<N>.png after each round with SHOT=1, and "SIDECOVER_DONE <shown>/<total>" at the end.
-- WATCH: more addresses to log (entries reached on the way, e.g. continuations); PREP: a route run once first.
-- Globals: HOOK (exec address), PTR (address of the pointer's low word, default 0x34), BANK (address of its bank
--          byte, default PTR + 2; engine B: PTR 0x7E4A37, BANK 0x7E4A39), OFFSET (optional word that must be 0, i.e.
--          the reader is at the start of a string; engine B 0x7E4A35), LO, HI (CPU range), TARGETS
--          ("DAE003,DAE017,..."), KEYS (route string), STALL (default 4), SHOT, SHOT_DELAY (shoot that many frames
--          into each round instead of at its end, e.g. while a description box is open).
local M = emu.memType.snesMemory
local function rd(a) return emu.read(a, M) end
local ptrAt, stall = PTR or 0x34, STALL or 4
local bankAt = BANK or (ptrAt + 2)

local targets, want, seen = {}, {}, {}
for h in string.gmatch(TARGETS, "%x+") do
  local a = tonumber(h, 16)
  targets[#targets + 1] = a
  want[a] = true
end
for h in string.gmatch(WATCH or "", "%x+") do want[tonumber(h, 16)] = true end
local nextT, shown, swapped, ready = 1, 0, 0, false

L.on_exec(HOOK, HOOK, function()
  if not ready then return end
  local p = rd(ptrAt) | (rd(ptrAt + 1) << 8) | (rd(bankAt) << 16)
  if p < LO or p >= HI or nextT > #targets then return end
  if OFFSET and (rd(OFFSET) | rd(OFFSET + 1)) ~= 0 then return end
  while nextT <= #targets and seen[targets[nextT]] do nextT = nextT + 1 end   -- read on the way (FF06 sub-strings)
  if nextT > #targets then return end
  local t = targets[nextT]
  nextT = nextT + 1
  swapped = swapped + 1
  emu.write(ptrAt, t & 0xFF, M); emu.write(ptrAt + 1, (t >> 8) & 0xFF, M); emu.write(bankAt, t >> 16, M)
  L.log(string.format("SWAP %06X f%d", t, L.frame))
end)

L.on_read(LO, HI - 1, function(addr)
  if want[addr] and not seen[addr] then
    seen[addr] = true
    shown = shown + 1
    L.log(string.format("TEXT %06X f%d", addr, L.frame))
  end
end)

local round, lastSwapped, idle, roundAt = 0, -1, 0, 0
L.on_frame(function()
  if SHOT == 1 and SHOT_DELAY and round > 0 and L.frame - roundAt == SHOT_DELAY then
    L.shot(string.format("round%03d.png", round))
  end
end)
local function queue(route)
  for step in string.gmatch(route, "[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    L.press(spec, tonumber(n))
  end
end
local function queue_keys()
  roundAt = L.frame
  queue(KEYS)
end
if PREP then queue(PREP) end
L.on_frame(function()
  if not L.route_done() then return end
  ready = true
  if round > 0 then
    if SHOT == 1 and not SHOT_DELAY then L.shot(string.format("round%03d.png", round)) end
    if swapped == lastSwapped then idle = idle + 1 else idle = 0 end
    lastSwapped = swapped
    if nextT > #targets or idle >= stall then
      local hit = 0
      for _, t in ipairs(targets) do if seen[t] then hit = hit + 1 end end
      L.log(string.format("SIDECOVER_DONE %d/%d swapped %d read %d f%d", hit, #targets, swapped, shown, L.frame))
      L.finish(0)
      return
    end
  end
  round = round + 1
  queue_keys()
end)
