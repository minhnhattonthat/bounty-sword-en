-- Side-table coverage runner (Mesen, via emu.py --state-in STATE --script; driven by tools/debug/sidecover.py).
-- Starts on a menu that draws a table's strings through a drawer whose source pointer sits in direct-page RAM
-- (the C1 string run C1:8E90 -> C1Run34 reads its pointer from $34-$36). Every call of HOOK whose pointer lies in
-- [LO, HI) gets the next TARGETS address instead, and KEYS (a route, "6 down;40 -") is pressed over and over to make
-- the menu redraw, until every target has been drawn or STALL rounds pass with no new one.
-- Logs "TEXT <addr> f<frame>" when the game reads a target's first byte (scripts/textcover.py), "SWAP <addr>" per
-- swap, a shot round<N>.png after each round with SHOT=1, and "SIDECOVER_DONE <shown>/<total>" at the end.
-- ONCE=1: at most one swap a round (the round's later keys, e.g. cursor moves, are for that script).
-- POKES: "7E4D1B:07FF,..." bytes written at every swap (empty FF07 sub-strings for the RAM names a script calls).
-- WATCH: more addresses to log (entries reached on the way, e.g. continuations); PREP: a route run once first.
-- Globals: HOOK (exec address), PTR (address of the pointer's low word, default 0x34), BANK (address of its bank
--          byte, default PTR + 2; engine B: PTR 0x7E4A37, BANK 0x7E4A39, hooked where a caller stores them),
--          LO, HI (CPU range), CLO, CHI (range the pointer must be in to be swapped, default LO/HI: a job can
--          catch a description pointer and swap in another table's entry), TARGETS
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
local roundSwaps = 0   -- ONCE=1: one swap a round (the round's later keys belong to that script, e.g. cursor moves)

L.on_exec(HOOK, HOOK, function()
  if not ready or (ONCE == 1 and roundSwaps > 0) then return end
  local p = rd(ptrAt) | (rd(ptrAt + 1) << 8) | (rd(bankAt) << 16)
  if p < (CLO or LO) or p >= (CHI or HI) or nextT > #targets then return end
  while nextT <= #targets and seen[targets[nextT]] do nextT = nextT + 1 end   -- read on the way (FF06 sub-strings)
  if nextT > #targets then return end
  local t = targets[nextT]
  nextT = nextT + 1
  swapped = swapped + 1
  roundSwaps = roundSwaps + 1
  emu.write(ptrAt, t & 0xFF, M); emu.write(ptrAt + 1, (t >> 8) & 0xFF, M); emu.write(bankAt, t >> 16, M)
  for a, hex in string.gmatch(POKES or "", "(%x+):(%x+)") do       -- RAM strings the swapped script FF06-calls
    local base = tonumber(a, 16)
    for i = 0, #hex / 2 - 1 do emu.write(base + i, tonumber(hex:sub(2 * i + 1, 2 * i + 2), 16), M) end
  end
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
  roundSwaps = 0
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
    -- the last swap's own keys run in the round after it, so finish only once a round adds no swap
    if (nextT > #targets and idle >= 1) or idle >= stall then
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
