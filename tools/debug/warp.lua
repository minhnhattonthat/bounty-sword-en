-- Bounty Sword debug warp (Mesen, via emu.py --script). Cold boot -> any scene in tools/debug/scenes.tsv.
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='scen_31'" --frames 3000 --sheet
-- Globals: SCENE (row name), SCENES (tsv path; default <repo>/tools/debug/scenes.tsv found from --out under work/),
--          MSG (override the msg column), MSGPTR (msg kind: swap in any engine A script by its 24-bit CPU
--          pointer instead, e.g. a side-table prompt: --var "MSGPTR=0xC41393"), HOLD (frames to run after the expected mode is reached, default the row's),
--          WARP_STATE (absolute path: save a state at SCENE_OK; only then, so a failed warp never leaves a bad state),
--          KEEP (don't stop at SCENE_OK; run on to --frames, e.g. to watch a scene play out).
-- How it works (docs/re/debug.md): the main loop runs the 24-bit continuation at $00EB-$00ED every frame. Once the
-- game's first mode is up, we point it at the leftover SCENARIO select (C0:D8B8, unreferenced debug code). When the
-- select reaches its input loop (C0:D9E5) we write the map number ($7FFD36) and then either take the select's own
-- "confirm" path (C0:D9F1: fade, load scenario, briefing -> chapter card -> battle map) or request a game mode
-- ($7E249A = mode, $7E2496 = 1). Kind "msg" also swaps the first dialogue the game starts for master message MSG
-- (hook at C2:4588, after C2:4561 has copied the message pointer to $7E3723-3725).
-- Columns: name kind(boot|scenario|mode|msg) map mode msg expect hold frames route mash then sav note ("sav" is for
-- warp_all.py, which boots that row with --sav). "route" is queued at
-- the warp, "then" when the expected mode is first reached (both "N buttons;N buttons"); "mash" is "key[,key..]:gap".
-- Log lines: "WARP <scene> f<frame>", "MODE <n> f<frame>" on every mode change (with a shot mode<n>.png HOLD/2 later),
-- "SCENE_OK <scene> f<frame>" once the expected mode has held for HOLD frames, then the run stops.
-- A row that never reaches its mode logs nothing more; tools/debug/warp_all.py treats a missing SCENE_OK as a failure.
local M = emu.memType.snesMemory
local function rd(a) return emu.read(a, M) end
local function rd16(a) return rd(a) | (rd(a + 1) << 8) end
local function wr16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end
local function EB() return rd(0xEB) | (rd(0xEC) << 8) | (rd(0xED) << 16) end
local function setEB(a) emu.write(0xEB, a & 0xFF, M); emu.write(0xEC, (a >> 8) & 0xFF, M); emu.write(0xED, a >> 16, M) end

local MODE_ADDR, MODE_REQ, MAP = 0x7E249A, 0x7E2496, 0x7FFD36
local SELECT_INIT, SELECT_LOOP, SELECT_GO = 0xC0D8B8, 0xC0D9E5, 0xC0D9F1
local MSG_HOOK, MSG_PTR, MSG_TABLE = 0xC24588, 0x7E3723, 0xE6D5EF

-- scene row
local function exists(p) local f = io.open(p, "r"); if f then f:close() end; return f ~= nil end
local path = SCENES
if not path then  -- Mesen's working folder varies: try the repo root above --out (work/...), then tools/mesen
  local root = (OUT or ""):gsub("\\", "/"):match("^(.*)/work/")
  for _, p in ipairs({ root and (root .. "/tools/debug/scenes.tsv"), "../debug/scenes.tsv", "tools/debug/scenes.tsv" }) do
    if p and exists(p) then path = p; break end
  end
end
assert(path, "scenes.tsv not found: pass --var \"SCENES=[[<repo>/tools/debug/scenes.tsv]]\"")
local row, cols
for line in io.lines(path) do
  local f = {}
  for v in (line .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = v end
  if not cols then cols = f
  elseif f[1] == SCENE then row = {}; for i, c in ipairs(cols) do row[c] = f[i] or "" end end
end
assert(row, "scene not in " .. path .. ": " .. tostring(SCENE))
local kind = row.kind
local map = tonumber(row.map) or 0
local mode = tonumber(row.mode)
local expect = tonumber(row.expect)
local msg = MSG or tonumber(row.msg)
local hold = HOLD or tonumber(row.hold) or 120

local function queue_route(spec)
  if not spec or spec == "" or spec == "-" then return end
  for step in spec:gmatch("[^;]+") do
    local n, b = step:match("^%s*(%d+)%s+(%S+)%s*$")
    assert(n, "bad route step in scene " .. SCENE .. ": " .. step)
    L.press(b, tonumber(n))
  end
end
local function queue_mash(spec)  -- "a:40" = press a for 6 frames every 40 until the run ends; "a,a,start:40" cycles keys
  if not spec or spec == "" or spec == "-" then return end
  local keys, gap = spec:match("^(%S+):(%d+)$")
  assert(keys, "bad mash in scene " .. SCENE .. ": " .. spec)
  local list = {}
  for k in keys:gmatch("[^,]+") do list[#list + 1] = k end
  for i = 1, 600 do L.press("-", tonumber(gap) - 6); L.press(list[(i - 1) % #list + 1], 6) end
end

local state = (kind == "boot") and "warped" or "boot"
local upFrames, warpedAt = 0, nil
local lastMode, reachedAt, shotAt = -1, nil, {}
local msgDone = false

if kind == "boot" then queue_route(row.route); queue_mash(row.mash); warpedAt = 0; L.log("WARP " .. SCENE .. " f0") end

if kind == "msg" then
  L.on_exec(MSG_HOOK, MSG_HOOK, function()
    if msgDone or state ~= "warped" then return end
    local p = MSG_TABLE + msg * 3
    local ptr = MSGPTR or (rd(p) | (rd(p + 1) << 8) | (rd(p + 2) << 16))
    emu.write(MSG_PTR, ptr & 0xFF, M); emu.write(MSG_PTR + 1, (ptr >> 8) & 0xFF, M); emu.write(MSG_PTR + 2, ptr >> 16, M)
    msgDone = L.frame
    L.log(string.format("MSG %d ptr %06X f%d", MSGPTR and -1 or msg, ptr, L.frame))
  end)
end

-- APU handshake nudge: after a scenario-select warp the sound CPU sometimes never echoes a command on port 1, and
-- C2:F59F (send-and-wait, both ROMs) spins at C2:F5A2-F5AE forever (the shop froze after its greeting). After
-- APU_SPIN polls with no answer we make the wait counter $D9 equal the port value, so the game moves on (debug only).
local APU_CMP, APU_SPIN = 0xC2F5AC, 4000
local apuSpins = 0
L.on_exec(APU_CMP, APU_CMP, function()
  if state ~= "warped" then return end
  apuSpins = apuSpins + 1
  if apuSpins < APU_SPIN then return end
  local s = emu.getState()
  local dp = (s["cpu.d"] or 0) + 0xD9
  emu.write(dp, (s["cpu.a"] or 0) & 0xFF, M)
  apuSpins = 0
  L.log(string.format("APU_NUDGE f%d", L.frame))
end)
L.on_exec(0xC2F5B0, 0xC2F5B0, function() apuSpins = 0 end)

L.on_frame(function(f)
  local m = rd16(MODE_ADDR)
  if state == "boot" then
    -- safe once the game's first mode (boot/intro) has run its init for a while
    if m ~= 0 then upFrames = upFrames + 1 end
    if upFrames >= 300 then setEB(SELECT_INIT); state = "select" end
  elseif state == "select" then
    if EB() == SELECT_LOOP then
      wr16(MAP, map)
      if kind == "scenario" or kind == "msg" then setEB(SELECT_GO)
      elseif kind == "mode" then wr16(MODE_ADDR, mode); wr16(MODE_REQ, 1)
      else error("unknown kind " .. tostring(kind)) end
      state = "warped"; warpedAt = f
      L.log("WARP " .. SCENE .. " f" .. f)
      queue_route(row.route); queue_mash(row.mash)
    end
  end
  if state ~= "warped" then return end
  if m ~= lastMode then
    lastMode = m
    L.log(string.format("MODE %d f%d map %d", m, f, rd16(MAP)))
    shotAt[f + hold // 2] = string.format("mode%02d.png", m)
    if expect and m == expect and not reachedAt then reachedAt = f; queue_route(row["then"]) end
  end
  if shotAt[f] then L.shot(shotAt[f]); shotAt[f] = nil end
  local ok = (expect == nil and f - warpedAt >= hold) or (reachedAt and f - reachedAt >= hold)
  if kind == "msg" then ok = msgDone and f - msgDone >= hold end  -- hold counts from the swapped message's start
  if ok and state ~= "done" then
    state = "done"
    L.shot("proof.png")
    L.log("SCENE_OK " .. SCENE .. " f" .. f)
    for a, v in (ASSERT or ""):gmatch("(%x+)=(%w+)") do  -- --var "ASSERT='7FFD36=45,7FF4E3=0xE7'": 16-bit RAM checks
      local got, want = rd16(tonumber(a, 16)), tonumber(v)
      L.log(string.format("ASSERT %s %s=%d (want %d)", got == want and "ok" or "FAIL", a, got, want))
    end
    if not KEEP then
      if WARP_STATE then L.save_state(WARP_STATE, function() L.finish(0) end) else L.finish(0) end
    end
  end
end)
