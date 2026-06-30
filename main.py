#!/usr/bin/env python3
# =============================================================================
# PICO-8 Favourites Sorter — muOS Edition  v1.7.4
# For: Anbernic RG Cube XX (720×720) running MustardOS
# Pure Python 3 + SDL2 via ctypes. No pip, no extras needed.
#
# Changelog:
#   v1.7.4 (2026-06-29) — Fix ZZ: v1.7.3's new duplicate-removal code used
#                                 list.remove(e), which matches by value
#                                 (dict equality) not identity. Two entries
#                                 with identical field values (a genuinely
#                                 duplicated raw line) could cause the wrong
#                                 object to be removed. Violates the project's
#                                 identity-removal rule. Rewrote as a single
#                                 identity-based filter pass — no .remove().
#   v1.7.3 (2026-06-29) — Sync YY: Pi version comparison audit.
#                                 Bug A: write_file unsorted order reversed vs
#                                   Pi. Pi writes raw unsorted (newest, prepend
#                                   stack) FIRST, then UNSORTED section bucket.
#                                   MU had them swapped — UNSORTED section came
#                                   first, burying newest entries below stale
#                                   UNSORTED section entries on reload. Fixed:
#                                   remaining = list(unsorted) + sections.get()
#                                 Bug B: _load() has no duplicate slug detection.
#                                   Pi warns and offers auto-remove. muOS now
#                                   silently deduplicates (first occurrence wins,
#                                   same Pi auto-remove logic) and appends count
#                                   to status. Prevents confusing state where the
#                                   same cart appears in two categories.
#                                 Bug C: _sg_build_cards passes full _sg_tag_cache
#                                   to suggest_new_categories_from_tags regardless
#                                   of current scope. Pi filters cache to only
#                                   entries in current pool before passing. When
#                                   scope is "unsorted" but cache was built in
#                                   "all" mode, categorised entries polluted the
#                                   unsorted suggestions. Fixed: filter cache to
#                                   pool in _sg_build_cards matching Pi logic.
#   v1.7.2 (2026-06-29) — Fix XX: Missing `import time` — crash on any
#                                 call to time.monotonic() (marquee scroll,
#                                 BBS fetch watchdog, toast, suggest BBS
#                                 watchdog). App booted but crashed the
#                                 moment marquee activated (highlighted item
#                                 in any panel) or BBS fetch started.
#                                 Fixed: `time` added to top-level imports.
#   v1.7.1 (2026-06-29) — Feature WW: Rename category, Delete category,
#                                 duplicate detection on assign.
#                                 Rename: X menu (when cat open) -> Rename
#                                   category -> VKeyboard pre-filled with
#                                   current name. Validates: non-empty, not
#                                   already existing. Updates categories[],
#                                   sections key, sel_cat live.
#                                 Delete: X menu -> Delete category ->
#                                   confirm dialog. On confirm: entries sorted
#                                   author A->Z (Pi version rule), prepended
#                                   to self.unsorted. sel_cat cleared, focus
#                                   returned to cats panel.
#                                 Duplicate detection: _assign() now checks
#                                   if slug already in target category. If so,
#                                   shows confirm dialog 'may already be here'
#                                   rather than silently moving (Pi deduped
#                                   silently; we warn instead).
#                                 Action menu is now context-aware: Rename
#                                   category and Delete category only appear
#                                   when sel_cat is set.
#   v1.7.0 (2026-06-29) — Feature VV: Suggest New Categories.
#                                 Ports Pi version _on_suggest_categories
#                                 to controller-native muOS design.
#                                 Data: TAG_TO_NEW_CAT, KEYWORD_TO_NEW_CAT,
#                                   MIN_SUGGEST=3, suggest_new_categories(),
#                                   suggest_new_categories_from_tags().
#                                 Screens: S_SUGGEST (card list), S_SGFETCH
#                                   (BBS fetch progress for suggest).
#                                 Controls on S_SUGGEST:
#                                   A = toggle card selected/deselected
#                                   X = rename card via VKeyboard
#                                   Y = toggle scope (Unsorted / All)
#                                   L2 = start BBS fetch (S_SGFETCH)
#                                   L1/R1 = page up/down
#                                   START = apply + create categories
#                                   B = cancel
#                                 Apply: creates categories, moves entries
#                                   by identity, rebuilds flat list.
#                                 BBS fetch: own queue (_sg_bbs_q), tag
#                                   cache (_sg_tag_cache), scaled watchdog,
#                                   drains per frame from draw().
#                                 Marquee on selected card name.
#   v1.6.4 (2026-06-29) — Sync UU: Ported fixes from stable Pi version.
#                                 Fix 1: parse_entry now includes 'base'
#                                   field (parts[2]) — the BBS cart ID.
#                                   This was the root crash cause: BBS
#                                   _worker used e['base'] which didn't
#                                   exist. Title fallback also uses base.
#                                 Fix 2: AUTO_SORT_RULES changed to dict
#                                   format {titles:[...], authors:[]}
#                                   matching Pi version structure.
#                                 Fix 3: auto_suggest_category now checks
#                                   author keywords as well as title,
#                                   matching Pi version behaviour.
#                                 Fix 4: BBS watchdog scaled to pool size
#                                   max(30, total*2+10)s — Pi version.
#                                 Fix 5: e['base'] restored in BBS worker
#                                   now that base field exists in entries.
#   v1.6.3 (2026-06-29) — Fix TT: Crash logging added. draw() and handle()
#                                 wrapped in try/except. Any exception is
#                                 logged to /tmp/pico8sorter_crash.log with
#                                 full traceback. App recovers to S_MAIN
#                                 instead of dying silently. Also fixed
#                                 e["base"] KeyError in BBS _worker — field
#                                 does not exist; replaced with e["slug"]
#                                 which is the PICO-8 cart ID used as BBS pid.
#   v1.6.2 (2026-06-29) — Fix SS: check_network() incorrectly blocked BBS
#                                 fetch when WiFi was working. Many Anbernic
#                                 WiFi drivers report operstate='unknown' even
#                                 when fully connected (RFC 2863 not impl).
#                                 Fix: muOS device config file is now checked
#                                 first (written by muOS network daemon, most
#                                 reliable). sysfs fallback now only treats
#                                 explicit 'down'/'notpresent'/'lowerlayerdown'
#                                 as offline — 'unknown'/'dormant' pass through
#                                 and let the fetch attempt naturally.
#   v1.6.1 (2026-06-29) — Fix RR: BBS fetch crashed the app.
#                                 check_network() was blocking the SDL main
#                                 thread for up to 2s doing a real HTTP HEAD
#                                 request. muOS foreground watchdog kills apps
#                                 that stop processing SDL events. Removed the
#                                 pre-flight check entirely — fetch_bbs_tags()
#                                 already catches all network errors per entry
#                                 and returns [] so a dead connection completes
#                                 gracefully with zero results. _bbs_finish now
#                                 shows a WiFi toast when _bbs_done==0.
#   v1.6.0 (2026-06-29) — Feature QQ: Marquee scroll for long text.
#                                 Highlighted game titles (left+right panels)
#                                 and category names (cats panel) scroll left
#                                 when text overflows the column width.
#                                 Timeline: 1s pause -> scroll at 60px/s ->
#                                 1s pause -> reset -> repeat. Implemented via
#                                 Renderer.text_marquee() which slices the SDL
#                                 texture source rect by scroll offset — no
#                                 clip rect or extra surfaces needed. State:
#                                 _mq_key tracks (panel,idx); _mq_start is
#                                 reset on key change or panel switch.
#                                 Non-overflowing text uses text_clip as before.
#   v1.5.6 (2026-06-29) — UI PP: Left panel header stacked.
#                                 Mode label ([ NEW/UNSORTED ] / [ ALL ENTRIES ])
#                                 now takes full width on line 1. Count badge
#                                 and sort indicator share line 2 beneath it —
#                                 count left-aligned, sort right-aligned.
#                                 LIST_Y non-browse adjusted to _sy(38).
#   v1.5.5 (2026-06-29) — Fix OO: Auto-sort crash on entry selection.
#                                 _draw_autosort passed hex int 0x1A1A3A to
#                                 R.fill() instead of an RGBA tuple. _sc()
#                                 does SDL_SetRenderDrawColor(*col) which
#                                 unpacks the colour — unpacking an int raises
#                                 TypeError, crashing immediately when the
#                                 cursor landed on any row. Fixed: replaced
#                                 with SEL_BG. Also fixed toast background
#                                 0x1A0A0A -> (26,10,10,255).
#   v1.5.4 (2026-06-29) — Fix NN: Bold font (fbd) is taller than the old
#                                 fsm it replaced, causing overlaps in four
#                                 places after v1.5.3:
#                                 Bug B: title/author overlap in left panel
#                                   (both modes) — author shifted to _sy(24).
#                                 Bug D: browse mode fbd header overlapping
#                                   sort indicator — sort moved to _sy(28),
#                                   LIST_Y browse to _sy(44).
#                                 Bug E: non-browse list start too close to
#                                   fbd header — LIST_Y moved to _sy(30).
#                                 Bug F: right panel and cats panel rows
#                                   starting at _sy(28) with 0-1px gap after
#                                   fbd header — rows moved to _sy(30).
#                                 Note: keyboard prompt changed from flg to
#                                   fbd (saves vertical space in dialog).
#   v1.5.3 (2026-06-29) — Polish MM: Bold font for titles and headers.
#                                 BOLD_FONT_PATHS added — tries BPreplayBold.otf
#                                 (muOS system font), DejaVuSans-Bold, Liberation
#                                 Sans-Bold in order. Falls back to regular font
#                                 if none found. Renderer gains fbd (bold medium)
#                                 and fbg (bold large). Used for: game titles in
#                                 all three panels, category names, panel headers,
#                                 screen titles, action/confirm dialog headings,
#                                 autosort suggestion titles.
#   v1.5.2 (2026-06-29) — Polish LL: Contrast/readability pass on all colours.
#                                 BG darker (17->10) for more panel separation.
#                                 DIM massively increased (80->160) — was near-
#                                 invisible on dark panels; now clearly readable.
#                                 TEAL brightened (74->100) for author text.
#                                 RED brightened (180->255) for errors/confirm.
#                                 PURPLE brightened for active category highlight.
#                                 ACCENT, YELLOW, WHITE, GREEN all lifted slightly.
#   v1.5.1 (2026-06-29) — Fix KK: _as_scroll() hardcoded vis=8 did not
#                                 match _draw_autosort's scaled vis formula.
#                                 On 480p devices (SH=480) draw shows ~5 rows
#                                 but scroll assumed 8 — cursor could sit on
#                                 rows that were never rendered. Fixed: both
#                                 _as_scroll and L1/R1 page-jump now compute
#                                 vis = max(4,(bh-_sy(40))//max(1,_sy(54)))
#                                 matching _draw_autosort exactly.
#   v1.5.0 (2026-06-29) — Port JJ: Multi-device support.
#                                 load_sdl_map() reads /opt/muos/device/config/
#                                 board/sdl_map at startup and populates all
#                                 JOY_* constants from the CSV. Falls back to
#                                 CubeXX-H defaults silently. Covers the two
#                                 L2/R2 variants across all 10 muOS devices.
#                                 detect_screen_size() reads screen/internal/
#                                 width+height from muOS device config; falls
#                                 back to SDL_GetCurrentDisplayMode post-init,
#                                 then 720x720. _SX/_SY scale factors drive
#                                 _sx()/_sy() helpers used throughout all draw
#                                 methods. Font sizes, panel coords, row heights,
#                                 VISIBLE counts, keyboard, action/confirm
#                                 dialogs, BBS fetch overlay, autosort list,
#                                 toast, and scrollbars all scale automatically.
#   v1.4.2 (2026-06-29) — Fix II: No-WiFi toast notification. check_network()
#                                 probes lexaloffle.com with a 2s HEAD request
#                                 before launching the BBS fetch thread. On
#                                 failure a red toast overlay appears at the
#                                 bottom of the screen for 4 seconds with the
#                                 reason (no network / timeout / error). If
#                                 keyword suggestions exist they are shown
#                                 instead; otherwise the status bar shows the
#                                 error. Toast system added to _draw_main_bg
#                                 and auto-clears on expiry.
#   v1.4.1 (2026-06-29) — Fix HH: Bug A: S_BBSFETCH never auto-transitioned to
#                                 S_AUTOSORT. draw() drained the 'done' queue msg
#                                 but ignored the return value; _h_bbsfetch then
#                                 drained an empty queue and saw done=False.
#                                 Fix: screen transition moved into _drain_bbs_queue
#                                 via new _bbs_finish() helper. _h_bbsfetch
#                                 simplified to B=cancel only.
#                                 Bug C: sel_entry not cleared after auto-sort
#                                 assign — right panel showed stale data. Fixed
#                                 in _as_apply_one and _as_apply_all.
#                                 Bug D: L1/R1 page-jump not handled in S_AUTOSORT.
#                                 Added L/R page by 8 in _h_autosort; hint updated.
#   v1.4.0 (2026-06-26) — Port GG: Auto-sort and BBS tag fetch ported from Pi version.
#                                 AUTO_SORT_RULES: keyword match against title
#                                 assigns unsorted entries to categories instantly.
#                                 TAG_TO_CAT: 60+ BBS genre tags mapped to cats.
#                                 Fetch BBS Tags: daemon thread with ThreadPoolExecutor
#                                 (max 3 workers) fetches lexaloffle.com/bbs/?pid=<base>
#                                 per entry; results drain into SDL main loop via
#                                 queue.Queue() each frame -- no GLib, no crash risk.
#                                 30-entry watchdog prevents permanent hang.
#                                 S_AUTOSORT screen: scrollable suggestion list,
#                                 A=assign one, B=skip, X=apply all, START=done.
#                                 S_BBSFETCH screen: live progress bar, B=cancel.
#                                 No browser feature omitted (no browser on muOS).
#   v1.3.2 (2026-06-26) — Rename FF: "Remove entry" → "Delete game" throughout.
#                                 Confirm dialog and status messages updated to match.
#   v1.3.1 (2026-06-26) — Add EE: Category reorder — L2/R2 in the cats column
#                                 now moves the highlighted category up/down in
#                                 self.categories, changing section order on save.
#                                 _move_cat() added.  Cats hint bar updated.
#   v1.3.0 (2026-06-26) — Remove DD: A/B swap feature removed entirely.
#                                 swap_ab flag, _resolve_btn, _do_swap_ab,
#                                 SWAP_AB event, START+SELECT combo, swap item
#                                 in action menu, and swap field in config.txt
#                                 all removed.  The feature was non-functional
#                                 and caused confusion about A/B roles.
#                                 cfg_load/cfg_save now handle path only.
#                                 fire() passes btn through to handle() directly.
#
#   v1.2.1 (2026-06-25) — Fix CC: r_scroll/r_idx not reset in _sort_cat();
#                                 sorted list appeared unchanged if scrolled.
#   v1.2.0 (2026-06-25) — Fix BB: NameError on L1/R1 in right panel — 'd' was
#                                 scoped inside F_LEFT block, referenced in F_RIGHT.
#   v1.1.9 (2026-06-25) — Fix Y: Rewrote to raw joystick API (GC API requires
#                                 GUID in gamecontrollerdb, not set for app launchers).
#                          Fix Z: JOY_* constants corrected from muOS sdl_map:
#                                 a:b3 b:b4 y:b5 x:b6 L1:b7 R1:b8 back:b9
#                                 start:b10 L2:b13 R2:b14 (digital on this device).
#   v1.1.7 (2026-06-25) — Fix R: browse scroll desync (VISIBLE_BROWSE=10 added).
#                          Fix S: unsorted entries written bare, no section header.
#   v1.1.6 (2026-06-25) — Fix N: _resolve_btn missing on App (crash every press).
#   v1.1.4 (2026-06-25) — Fix G/H/I: combo ordering, hat clear, L1/R1 no repeat.
#   v1.1.3 (2026-06-25) — Fix E/F: BTN_BACK 5→4; L2/R2 digital button approach.
#   v1.1.2 (2026-06-25) — Fix A/B/C/D: scroll, held-repeat, clamp, wrap.
#
# Features:
#   • NEW/UNSORTED list  ←→  ALL ENTRIES toggle (Y on left panel)
#   • ALL ENTRIES: sort by Name/Author/Category (Y cycles), live filter (X)
#   • Assign entry to category (A on entry → A on category)
#   • View category entries in right panel
#   • Reorder entries within a category (L2/R2 in right panel)
#   • Sort category A→Z by author/title (Y in right panel)
#   • Delete game permanently with confirmation (X → Delete Game)
#   • Add category (X → Add Category)
#   • Save + timestamped backup (START)
#   • Context-aware hint bar
#   • Auto-detect favourites.txt; falls back to keyboard path entry
#
# Controls:
#   D-pad        Navigate panels and lists
#   A            Select / Confirm / Open category
#   B            Clear selection / Back / Cancel
#   X            Action menu
#   Y            Toggle UNSORTED↔ALL  |  cycle sort  |  sort cat A→Z
#   L1 / R1      Page up / down
#   L2 / R2      Move entry up / down within category (right panel)
#   START        Save file immediately
#   SELECT       Quit to muOS
# =============================================================================

import ctypes, ctypes.util, os, re, shutil, sys, threading, queue, time
import urllib.request
from datetime import datetime

# =============================================================================
# SDL2 bootstrap
# =============================================================================

_sdl_name = ctypes.util.find_library("SDL2") or "libSDL2-2.0.so.0"
try:
    SDL = ctypes.CDLL(_sdl_name)
except OSError:
    sys.exit("ERROR: SDL2 not found.")

SDL_INIT_VIDEO    = 0x00000020
SDL_INIT_JOYSTICK = 0x00000200
SDL_QUIT_EVENT    = 0x100
SDL_KEYDOWN       = 0x300
# Raw joystick events — GameController API not used.
# Reason: SDL GC API requires the device GUID to exist in
# /usr/lib/gamecontrollerdb.txt, which muOS only populates when launching
# emulators (via CONFIGURE_RETROARCH).  For a standalone app launcher this
# is not guaranteed so SDL_IsGameController() returns false and all
# SDL_CONTROLLERBUTTONDOWN events are silent.
# DinguxCommander (reference impl) uses SDL_JoystickOpen(0) for the same reason.
SDL_JOYBUTTONDOWN_EV = 0x603
SDL_JOYBUTTONUP_EV   = 0x604
SDL_JOYHATMOTION_EV  = 0x602
SDL_HAT_UP=1; SDL_HAT_RIGHT=2; SDL_HAT_DOWN=4; SDL_HAT_LEFT=8; SDL_HAT_CENTERED=0
SDL_WINDOWPOS_CENTERED = 0x2FFF0000

SDLK_UP=1073741906; SDLK_DOWN=1073741905
SDLK_LEFT=1073741904; SDLK_RIGHT=1073741903
SDLK_RETURN=13; SDLK_ESCAPE=27; SDLK_BACKSPACE=8
SDLK_TAB=9

# Raw joystick button numbers — from the authoritative muOS internals file:
#   device/rgcubexx-h/config/board/sdl_map  (GUID 19000000010000000100000000010000)
#   a:b3 b:b4 y:b5 x:b6 leftshoulder:b7 rightshoulder:b8 back:b9 start:b10
#   guide:b11 leftstick:b12 lefttrigger:b13 righttrigger:b14 rightstick:b15
#   dpup:h0.1 dpdown:h0.4 dpleft:h0.8 dpright:h0.2
#   L2/R2 are digital buttons (b13/b14) on this device, not analog axes.
#   Button numbers and screen size are loaded at runtime from muOS device config.

# muOS device config paths
MUOS_SDL_MAP = "/opt/muos/device/config/board/sdl_map"
MUOS_SCR_W   = "/opt/muos/device/config/screen/internal/width"
MUOS_SCR_H   = "/opt/muos/device/config/screen/internal/height"

# CubeXX-H fallback defaults (desktop/non-muOS)
_JOY_DEFAULTS = {
    "a": 3, "b": 4, "y": 5, "x": 6,
    "leftshoulder": 7, "rightshoulder": 8,
    "back": 9, "start": 10,
    "leftstick": 12, "lefttrigger": 13, "righttrigger": 14, "rightstick": 15,
}

def load_sdl_map():
    m = dict(_JOY_DEFAULTS)
    try:
        with open(MUOS_SDL_MAP) as f:
            line = f.read().strip()
        for token in line.split(","):
            token = token.strip()
            if ":" in token and not token.startswith("platform"):
                name, binding = token.split(":", 1)
                if binding.startswith("b") and binding[1:].isdigit():
                    m[name.strip()] = int(binding[1:])
    except Exception:
        pass
    return m

def detect_screen_size():
    try:
        w = int(open(MUOS_SCR_W).read().strip())
        h = int(open(MUOS_SCR_H).read().strip())
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return 720, 720

_sdl_map = load_sdl_map()
SW, SH   = detect_screen_size()

JOY_A     = _sdl_map.get("a",              3)
JOY_B     = _sdl_map.get("b",              4)
JOY_Y     = _sdl_map.get("y",              5)
JOY_X     = _sdl_map.get("x",             6)
JOY_L     = _sdl_map.get("leftshoulder",   7)
JOY_R     = _sdl_map.get("rightshoulder",  8)
JOY_BACK  = _sdl_map.get("back",           9)
JOY_START = _sdl_map.get("start",         10)
JOY_L3    = _sdl_map.get("leftstick",     12)
JOY_L2    = _sdl_map.get("lefttrigger",   13)
JOY_R2    = _sdl_map.get("righttrigger",  14)
JOY_R3    = _sdl_map.get("rightstick",    15)

# Colours RGBA tuples
BG      = (10,  10,  16,  255)  # darker — more separation from panels
PANEL   = (28,  28,  42,  255)  # slightly lighter than before for contrast
ACCENT  = (0,   210, 240,  255)  # brighter cyan — focused borders, headers
YELLOW  = (255, 242,  60,  255)  # brighter yellow — titles, selected items
WHITE   = (240, 240, 255,  255)  # near-white — primary text
DIM     = (160, 160, 185,  255)  # was 80,80,100 — now much more readable
SEL_BG  = (50,  35, 110,  255)  # slightly brighter selection highlight
GREEN   = (50,  230, 110,  255)  # brighter green
RED     = (255,  70,  70,  255)  # brighter red — errors, confirm dialogs
PURPLE  = (140, 100, 220,  255)  # brighter purple — active category
TEAL    = (100, 200, 220,  255)  # brighter teal — author text, categories
ORANGE  = (255, 165,  50,  255)  # brighter orange

# SW/SH set above by detect_screen_size(). Layout scales from 720x720 base.
FPS     = 30

# Scale factor relative to 720x720 reference resolution.
# 640x480 devices get SX~0.889, SY~0.667 — everything reflows proportionally.
_SX = SW / 720.0
_SY = SH / 720.0

def _sx(n): return max(1, int(n * _SX))
def _sy(n): return max(1, int(n * _SY))

ROW_H          = _sy(44)
VISIBLE        = max(5, (SH - _sy(110)) // ROW_H)
VISIBLE_BROWSE = max(4, (SH - _sy(130)) // _sy(54))

# =============================================================================
# SDL2 structs
# =============================================================================

class Rect(ctypes.Structure):
    _fields_ = [("x",ctypes.c_int),("y",ctypes.c_int),
                ("w",ctypes.c_int),("h",ctypes.c_int)]

class Color(ctypes.Structure):
    _fields_ = [("r",ctypes.c_uint8),("g",ctypes.c_uint8),
                ("b",ctypes.c_uint8),("a",ctypes.c_uint8)]

class _KeySym(ctypes.Structure):
    _fields_ = [("scancode",ctypes.c_int32),("sym",ctypes.c_int32),
                ("mod",ctypes.c_uint16),("unused",ctypes.c_uint32)]

class _KeyEvent(ctypes.Structure):
    _fields_ = [("type",ctypes.c_uint32),("timestamp",ctypes.c_uint32),
                ("windowID",ctypes.c_uint32),("state",ctypes.c_uint8),
                ("repeat",ctypes.c_uint8),("pad2",ctypes.c_uint8),
                ("pad3",ctypes.c_uint8),("keysym",_KeySym)]

class _CBtnEvent(ctypes.Structure):
    _fields_ = [("type",ctypes.c_uint32),("timestamp",ctypes.c_uint32),
                ("which",ctypes.c_int32),("button",ctypes.c_uint8),
                ("state",ctypes.c_uint8),("pad1",ctypes.c_uint8),
                ("pad2",ctypes.c_uint8)]

class _JoyHatEvent(ctypes.Structure):
    _fields_ = [("type",ctypes.c_uint32),("timestamp",ctypes.c_uint32),
                ("which",ctypes.c_int32),("hat",ctypes.c_uint8),
                ("value",ctypes.c_uint8),("pad1",ctypes.c_uint8),
                ("pad2",ctypes.c_uint8)]

class Event(ctypes.Union):
    _fields_ = [("type",ctypes.c_uint32),("key",_KeyEvent),
                ("cbutton",_CBtnEvent),
                ("jhat",_JoyHatEvent),("pad",ctypes.c_uint8*56)]

# SDL function signatures
SDL.SDL_Init.argtypes=[ctypes.c_uint32]; SDL.SDL_Init.restype=ctypes.c_int
SDL.SDL_CreateWindow.restype=ctypes.c_void_p
SDL.SDL_CreateRenderer.restype=ctypes.c_void_p
SDL.SDL_CreateTextureFromSurface.restype=ctypes.c_void_p
SDL.SDL_QueryTexture.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]
SDL.SDL_RenderCopy.argtypes=[ctypes.c_void_p,ctypes.c_void_p,
    ctypes.POINTER(Rect),ctypes.POINTER(Rect)]
SDL.SDL_DestroyTexture.argtypes=[ctypes.c_void_p]
SDL.SDL_FreeSurface.argtypes=[ctypes.c_void_p]
SDL.SDL_PollEvent.argtypes=[ctypes.POINTER(Event)]; SDL.SDL_PollEvent.restype=ctypes.c_int
SDL.SDL_GetTicks.restype=ctypes.c_uint32
SDL.SDL_Delay.argtypes=[ctypes.c_uint32]
SDL.SDL_JoystickEventState.argtypes=[ctypes.c_int]; SDL.SDL_JoystickEventState.restype=ctypes.c_int
SDL.SDL_SetRenderDrawColor.argtypes=[ctypes.c_void_p,ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint8]
SDL.SDL_SetRenderDrawColor.restype=ctypes.c_int
SDL.SDL_RenderClear.argtypes=[ctypes.c_void_p]; SDL.SDL_RenderClear.restype=ctypes.c_int
SDL.SDL_RenderFillRect.argtypes=[ctypes.c_void_p,ctypes.POINTER(Rect)]; SDL.SDL_RenderFillRect.restype=ctypes.c_int
SDL.SDL_RenderDrawRect.argtypes=[ctypes.c_void_p,ctypes.POINTER(Rect)]; SDL.SDL_RenderDrawRect.restype=ctypes.c_int
SDL.SDL_RenderDrawLine.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]; SDL.SDL_RenderDrawLine.restype=ctypes.c_int
SDL.SDL_RenderPresent.argtypes=[ctypes.c_void_p]; SDL.SDL_RenderPresent.restype=None

# TTF
_ttf_name = ctypes.util.find_library("SDL2_ttf") or "libSDL2_ttf-2.0.so.0"
try:
    TTF = ctypes.CDLL(_ttf_name)
    TTF.TTF_Init.restype=ctypes.c_int
    TTF.TTF_OpenFont.restype=ctypes.c_void_p
    TTF.TTF_OpenFont.argtypes=[ctypes.c_char_p,ctypes.c_int]
    TTF.TTF_RenderUTF8_Blended.restype=ctypes.c_void_p
    TTF.TTF_RenderUTF8_Blended.argtypes=[ctypes.c_void_p,ctypes.c_char_p,Color]
    TTF.TTF_SizeUTF8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]
    TTF.TTF_SizeUTF8.restype=ctypes.c_int
    TTF.TTF_CloseFont.argtypes=[ctypes.c_void_p]
    HAS_TTF = TTF.TTF_Init()==0
except OSError:
    HAS_TTF = False

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
    "/opt/muos/default/font/BPreplayBold.otf",
]

# Bold font — muOS ships BPreplayBold; fall back to DejaVuSans-Bold or regular
BOLD_FONT_PATHS = [
    "/opt/muos/default/font/BPreplayBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
]

def find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

def find_bold_font():
    for p in BOLD_FONT_PATHS:
        if os.path.exists(p):
            return p
    return None  # caller falls back to regular font

# =============================================================================
# Renderer
# =============================================================================

class Renderer:
    def __init__(self, win, rend, font_path, bold_path=None):
        self.win  = win
        self.rend = rend
        self._cache = {}
        self.fsm = self.fmd = self.flg = None
        self.fbd = self.fbg = None   # bold medium, bold large
        if HAS_TTF and font_path:
            fp = font_path.encode()
            self.fsm = TTF.TTF_OpenFont(fp, _sy(15))
            self.fmd = TTF.TTF_OpenFont(fp, _sy(19))
            self.flg = TTF.TTF_OpenFont(fp, _sy(25))
            # Bold fonts — fall back to regular if bold not available
            bp = (bold_path or font_path).encode()
            self.fbd = TTF.TTF_OpenFont(bp, _sy(19)) or self.fmd
            self.fbg = TTF.TTF_OpenFont(bp, _sy(25)) or self.flg

    def _sc(self, col):
        SDL.SDL_SetRenderDrawColor(self.rend, *col)

    def clear(self):
        self._sc(BG); SDL.SDL_RenderClear(self.rend)

    def fill(self, x, y, w, h, col):
        self._sc(col)
        SDL.SDL_RenderFillRect(self.rend, ctypes.byref(Rect(x,y,w,h)))

    def box(self, x, y, w, h, col):
        self._sc(col)
        SDL.SDL_RenderDrawRect(self.rend, ctypes.byref(Rect(x,y,w,h)))

    def hline(self, x, y, w, col):
        self._sc(col)
        SDL.SDL_RenderDrawLine(self.rend, x, y, x+w, y)

    # FIX(bug6): cap the texture cache to avoid unbounded memory growth when
    # scrolling large lists.  512 entries covers normal usage; oldest entries
    # are evicted first (insertion-order dict, Python 3.7+).
    _CACHE_MAX = 512

    def _tex(self, txt, font, col):
        key = (txt, id(font), col)
        if key not in self._cache:
            # Evict oldest entry when the cap is reached
            if len(self._cache) >= self._CACHE_MAX:
                oldest_key, (old_tex, _, _) = next(iter(self._cache.items()))
                SDL.SDL_DestroyTexture(old_tex)
                del self._cache[oldest_key]
            c   = Color(*col)
            srf = TTF.TTF_RenderUTF8_Blended(font, txt.encode("utf-8"), c)
            if not srf:
                return None, 0, 0
            tex = SDL.SDL_CreateTextureFromSurface(self.rend, srf)
            SDL.SDL_FreeSurface(srf)
            tw, th = ctypes.c_int(0), ctypes.c_int(0)
            SDL.SDL_QueryTexture(tex, None, None, ctypes.byref(tw), ctypes.byref(th))
            self._cache[key] = (tex, tw.value, th.value)
        else:
            # Move to end to maintain LRU order
            self._cache[key] = self._cache.pop(key)
        return self._cache[key]

    def text(self, txt, x, y, col=WHITE, font=None):
        if not HAS_TTF or not txt:
            return 0
        f = font or self.fmd
        if not f:
            return 0
        tex, tw, th = self._tex(txt, f, col)
        if not tex:
            return 0
        SDL.SDL_RenderCopy(self.rend, tex,
            ctypes.byref(Rect(0,0,tw,th)), ctypes.byref(Rect(x,y,tw,th)))
        return tw

    def text_w(self, txt, font=None):
        if not HAS_TTF or not txt:
            return len(txt)*9
        f = font or self.fmd
        if not f:
            return len(txt)*9
        tw, th = ctypes.c_int(0), ctypes.c_int(0)
        TTF.TTF_SizeUTF8(f, txt.encode("utf-8"), ctypes.byref(tw), ctypes.byref(th))
        return tw.value

    def text_clip(self, txt, x, y, maxw, col=WHITE, font=None):
        # FIX(perf): replace O(n²) char-by-char trim with binary search O(n log n).
        # For a 40-char string the old loop could call text_w up to 40 times;
        # binary search calls it at most ~6 times.
        if not txt:
            return
        if self.text_w(txt, font) <= maxw:
            self.text(txt, x, y, col, font)
            return
        lo, hi = 0, len(txt)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.text_w(txt[:mid], font) <= maxw:
                lo = mid
            else:
                hi = mid - 1
        if lo:
            self.text(txt[:lo], x, y, col, font)

    def text_marquee(self, txt, x, y, maxw, offset, col=WHITE, font=None):
        """Draw txt scrolled left by `offset` pixels, clipped to maxw.
        Uses source-rect slicing on the SDL texture — no clip rect needed.
        offset=0 shows the start of the text; positive offset scrolls left.
        Returns full text pixel width (so caller can compute max offset).
        """
        if not HAS_TTF or not txt:
            return 0
        f = font or self.fmd
        if not f:
            return 0
        tex, tw, th = self._tex(txt, f, col)
        if not tex or tw == 0:
            return 0
        if tw <= maxw:
            # Text fits — draw normally, no scroll needed
            SDL.SDL_RenderCopy(self.rend, tex,
                ctypes.byref(Rect(0,0,tw,th)), ctypes.byref(Rect(x,y,tw,th)))
            return tw
        # Clamp offset so we never show past the end of the texture
        offset = max(0, min(offset, tw - maxw))
        src = Rect(offset, 0, maxw, th)
        dst = Rect(x, y, maxw, th)
        SDL.SDL_RenderCopy(self.rend, tex,
            ctypes.byref(src), ctypes.byref(dst))
        return tw

    def present(self):
        SDL.SDL_RenderPresent(self.rend)

    def flush(self):
        for tex,_,_ in self._cache.values():
            SDL.SDL_DestroyTexture(tex)
        self._cache = {}

# =============================================================================
# PICO-8 favourites.txt parser/writer  (verbatim logic from v1.1.0)
# =============================================================================

DIVIDER_RE = re.compile(r"^#\s*={3,}")
CAT_RE     = re.compile(r"^#\s*([A-Z][^\n]*)$")

DEFAULT_CATS = [
    "CURRENT FAVORITES",
    "ROGUELIKES / DUNGEON CRAWLERS",
    "MOT COLLECTION",
    "SHOOTERS / SPACE GAMES",
    "PUZZLE GAMES",
    "RACING / FLYING / ACTION",
    "PLATFORMERS / ADVENTURE",
    "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "MUSIC / DEMOSCENE",
    "CLOCKS / UTILITIES / TOYS",
]

BBS_PREFIX = "http://www.lexaloffle.com/bbs/?pid="  # http: muOS has no system CA certs

TAG_TO_CAT = {
    "roguelike":        "ROGUELIKES / DUNGEON CRAWLERS",
    "dungeon-crawler":  "ROGUELIKES / DUNGEON CRAWLERS",
    "dungeon":          "ROGUELIKES / DUNGEON CRAWLERS",
    "rogue":            "ROGUELIKES / DUNGEON CRAWLERS",
    "turn-based":       "ROGUELIKES / DUNGEON CRAWLERS",
    "strategy":         "ROGUELIKES / DUNGEON CRAWLERS",
    "rpg":              "ROGUELIKES / DUNGEON CRAWLERS",
    "top-down":         "ROGUELIKES / DUNGEON CRAWLERS",
    "shooter":          "SHOOTERS / SPACE GAMES",
    "shoot-em-up":      "SHOOTERS / SPACE GAMES",
    "shmup":            "SHOOTERS / SPACE GAMES",
    "bullet-hell":      "SHOOTERS / SPACE GAMES",
    "space":            "SHOOTERS / SPACE GAMES",
    "arcade":           "SHOOTERS / SPACE GAMES",
    "action":           "SHOOTERS / SPACE GAMES",
    "puzzle":           "PUZZLE GAMES",
    "sokoban":          "PUZZLE GAMES",
    "tile-based":       "PUZZLE GAMES",
    "match-3":          "PUZZLE GAMES",
    "logic":            "PUZZLE GAMES",
    "block":            "PUZZLE GAMES",
    "racing":           "RACING / FLYING / ACTION",
    "driving":          "RACING / FLYING / ACTION",
    "flying":           "RACING / FLYING / ACTION",
    "flight":           "RACING / FLYING / ACTION",
    "fighting":         "RACING / FLYING / ACTION",
    "brawler":          "RACING / FLYING / ACTION",
    "platformer":       "PLATFORMERS / ADVENTURE",
    "platform":         "PLATFORMERS / ADVENTURE",
    "adventure":        "PLATFORMERS / ADVENTURE",
    "exploration":      "PLATFORMERS / ADVENTURE",
    "metroidvania":     "PLATFORMERS / ADVENTURE",
    "run-and-gun":      "PLATFORMERS / ADVENTURE",
    "runner":           "PLATFORMERS / ADVENTURE",
    "narrative":        "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "story":            "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "visual-novel":     "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "walking-sim":      "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "atmospheric":      "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "horror":           "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "art":              "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "music":            "MUSIC / DEMOSCENE",
    "rhythm":           "MUSIC / DEMOSCENE",
    "demoscene":        "MUSIC / DEMOSCENE",
    "demo":             "MUSIC / DEMOSCENE",
    "chiptune":         "MUSIC / DEMOSCENE",
    "audio":            "MUSIC / DEMOSCENE",
    "tool":             "CLOCKS / UTILITIES / TOYS",
    "utility":          "CLOCKS / UTILITIES / TOYS",
    "toy":              "CLOCKS / UTILITIES / TOYS",
    "clock":            "CLOCKS / UTILITIES / TOYS",
    "screensaver":      "CLOCKS / UTILITIES / TOYS",
    "generator":        "CLOCKS / UTILITIES / TOYS",
    "sandbox":          "CLOCKS / UTILITIES / TOYS",
}

AUTO_SORT_RULES = [
    ("ROGUELIKES / DUNGEON CRAWLERS", {
        "titles":  ["rogue","dungeon","crawl","rl","nethack","spelunk",
                    "tomb","crypt","lich","undead","dwarf","descent"],
        "authors": [],
    }),
    ("SHOOTERS / SPACE GAMES", {
        "titles":  ["shoot","bullet","shmup","space","galaxy","star",
                    "asteroid","invader","blaster","laser","alien","ufo",
                    "turret","missile","jet","pilot"],
        "authors": [],
    }),
    ("PUZZLE GAMES", {
        "titles":  ["puzzle","block","match","slide","sokoban","tetris",
                    "swap","connect","logic","nonogram","picross","sudoku","flow","pipe"],
        "authors": [],
    }),
    ("RACING / FLYING / ACTION", {
        "titles":  ["race","racing","drift","kart","drive","speed",
                    "fly","flight","wing","bird","brawl","fight","combat","action","beat"],
        "authors": [],
    }),
    ("PLATFORMERS / ADVENTURE", {
        "titles":  ["jump","platform","adventure","quest","explore",
                    "hero","knight","castle","world","land","island",
                    "climb","run","escape","maze"],
        "authors": [],
    }),
    ("ATMOSPHERIC / WALKING SIMS / NARRATIVE", {
        "titles":  ["walk","wander","story","narrative","visual novel",
                    "atmospheric","calm","relax","ambient","drift","dream","memory","journal"],
        "authors": [],
    }),
    ("MUSIC / DEMOSCENE", {
        "titles":  ["music","song","beat","drum","synth","audio",
                    "sound","demo","chip","tracker","melody","jukebox","radio","concert"],
        "authors": [],
    }),
    ("CLOCKS / UTILITIES / TOYS", {
        "titles":  ["clock","watch","timer","util","tool","toy",
                    "sandbox","screensaver","paint","draw","sketch","generator","test"],
        "authors": [],
    }),
]

def auto_suggest_category(entry, categories):
    """Return best matching category for entry via title and author keywords, or None.
    Matches Pi version: title keywords checked first, then author keywords.
    First matching category wins.
    """
    title  = entry["title"].lower()
    author = entry["author"].lower()
    for cat_name, rules in AUTO_SORT_RULES:
        if cat_name not in categories:
            continue
        for kw in rules["titles"]:
            if kw in title:
                return cat_name
        for kw in rules["authors"]:
            if kw in author:
                return cat_name
    return None

# muOS network state paths — sysfs operstate is instant, no blocking
_MUOS_NET_STATE_PATHS = [
    "/sys/class/net/wlan0/operstate",   # primary WiFi interface on all Anbernic muOS devices
    "/sys/class/net/wlan1/operstate",   # fallback for alternate interface name
]
# muOS device config network state (points to the same sysfs file via GET_VAR)
_MUOS_NET_CFG_STATE  = "/opt/muos/device/config/network/state"

def check_network():
    """Check WiFi state using muOS device config — instant, non-blocking file read.
    Returns (True, "") if network is up or unknown, (False, reason) if definitively down.

    Priority:
      1. /opt/muos/device/config/network/state — written by muOS network daemon,
         most reliable. Value is "up" when connected, "down" when not.
      2. /sys/class/net/wlan0/operstate — kernel sysfs. Note: many Anbernic WiFi
         drivers report "unknown" even when connected (RFC 2863 not implemented).
         We only treat explicit "down"/"notpresent"/"lowerlayerdown" as offline.
      3. Assume connected if no files readable (desktop/non-muOS).
    """
    # muOS device config is authoritative — check it first
    try:
        state = open(_MUOS_NET_CFG_STATE).read().strip().lower()
        if state == "up":
            return True, ""
        if state == "down":
            return False, "WiFi is not connected — enable WiFi in muOS settings"
        # Any other value (file empty, unexpected) — fall through to sysfs
    except OSError:
        pass

    # sysfs fallback — only treat explicit down states as offline
    # "unknown" is default on embedded drivers that don't update operstate
    for path in _MUOS_NET_STATE_PATHS:
        try:
            state = open(path).read().strip().lower()
            if state == "up":
                return True, ""
            if state in ("down", "notpresent", "lowerlayerdown"):
                return False, "WiFi is not connected — enable WiFi in muOS settings"
            # "unknown" or "dormant" or "testing" — assume up, let fetch try
        except OSError:
            continue

    # Could not read any state file — not on muOS or paths changed, assume up
    return True, ""

def fetch_bbs_tags(pid):
    """Fetch genre tags for one cart from Lexaloffle BBS. Returns [] on error.
    Network call - must be run off the main SDL thread.
    """
    url = BBS_PREFIX + pid
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; pico8-fav-sorter-muos)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode("utf-8", errors="replace")
        return re.findall(r'<span class="tag">(.*?)</span>', html)
    except Exception:
        return []

def bbs_tags_to_category(tags, categories):
    """Map BBS tags to first matching local category, or None."""
    for tag in tags:
        cat = TAG_TO_CAT.get(tag.lower())
        if cat and cat in categories:
            return cat
    return None

# ── Suggest-Categories data (new themes not in DEFAULT_CATS) ────────────────
MIN_SUGGEST = 3   # min entries sharing a theme before surfacing a suggestion

TAG_TO_NEW_CAT = {
    # Horror
    "horror":            "HORROR",
    "survival-horror":   "HORROR",
    # Sports
    "sports":            "SPORTS",
    "football":          "SPORTS",
    "soccer":            "SPORTS",
    "basketball":        "SPORTS",
    "baseball":          "SPORTS",
    "golf":              "SPORTS",
    "tennis":            "SPORTS",
    # Card / Board
    "card-game":         "CARD & BOARD GAMES",
    "board-game":        "CARD & BOARD GAMES",
    "tabletop":          "CARD & BOARD GAMES",
    "deck-building":     "CARD & BOARD GAMES",
    "poker":             "CARD & BOARD GAMES",
    "chess":             "CARD & BOARD GAMES",
    # Tower Defence
    "tower-defense":     "TOWER DEFENCE",
    "tower-defence":     "TOWER DEFENCE",
    "td":                "TOWER DEFENCE",
    # Simulation
    "simulation":        "SIMULATION",
    "sim":               "SIMULATION",
    "city-builder":      "SIMULATION",
    "farming":           "SIMULATION",
    "management":        "SIMULATION",
    # Multiplayer
    "multiplayer":       "MULTIPLAYER",
    "co-op":             "MULTIPLAYER",
    "2-player":          "MULTIPLAYER",
    "local-multiplayer": "MULTIPLAYER",
    # Idle / Clicker
    "idle":              "IDLE & CLICKER",
    "clicker":           "IDLE & CLICKER",
    "incremental":       "IDLE & CLICKER",
}

KEYWORD_TO_NEW_CAT = {
    "horror":    "HORROR",
    "zombie":    "HORROR",
    "haunt":     "HORROR",
    "creep":     "HORROR",
    "scary":     "HORROR",
    "terror":    "HORROR",
    "sport":     "SPORTS",
    "soccer":    "SPORTS",
    "footbal":   "SPORTS",
    "basket":    "SPORTS",
    "tennis":    "SPORTS",
    "golf":      "SPORTS",
    "chess":     "CARD & BOARD GAMES",
    "poker":     "CARD & BOARD GAMES",
    "card":      "CARD & BOARD GAMES",
    "tower def": "TOWER DEFENCE",
    "idle":      "IDLE & CLICKER",
    "clicker":   "IDLE & CLICKER",
    "farm":      "SIMULATION",
    "simul":     "SIMULATION",
    "tycoon":    "SIMULATION",
    "manage":    "SIMULATION",
}

def suggest_new_categories(entries, existing_categories):
    """Scan entries for themes not in existing_categories.
    Returns dict: proposed_cat_name -> [entry, ...] for groups >= MIN_SUGGEST.
    Uses title keyword matching only (instant, no network).
    """
    from collections import defaultdict
    buckets = defaultdict(list)
    existing_upper = {c.upper() for c in existing_categories}
    for entry in entries:
        title = entry["title"].lower()
        for kw, proposed in KEYWORD_TO_NEW_CAT.items():
            if kw in title and proposed.upper() not in existing_upper:
                buckets[proposed.upper()].append(entry)
                break
    return {cat: ents for cat, ents in buckets.items() if len(ents) >= MIN_SUGGEST}

def suggest_new_categories_from_tags(tag_cache, existing_categories):
    """Same as above but uses a pre-fetched tag_cache dict:
    id(entry) -> (entry, [tag, ...]) from a prior BBS fetch.
    Returns dict: proposed_cat_name -> [entry, ...] for groups >= MIN_SUGGEST.
    """
    from collections import defaultdict
    buckets = defaultdict(list)
    existing_upper = {c.upper() for c in existing_categories}
    for eid, (entry, tags) in tag_cache.items():
        for tag in tags:
            proposed = TAG_TO_NEW_CAT.get(tag.lower())
            if proposed and proposed.upper() not in existing_upper:
                buckets[proposed.upper()].append(entry)
                break
    return {cat: ents for cat, ents in buckets.items() if len(ents) >= MIN_SUGGEST}


SEARCH_PATHS = [
    # Confirmed muOS path — bind-mount (runtime, SD1 or SD2 aware)
    "/run/muos/storage/save/pico8/favourites.txt",
    # Direct SD card fallbacks
    "/mnt/mmc/MUOS/save/pico8/favourites.txt",
    "/mnt/sdcard/MUOS/save/pico8/favourites.txt",
    # pico-8 casing variant (older muOS releases)
    "/run/muos/storage/save/pico-8/favourites.txt",
    "/mnt/mmc/MUOS/save/pico-8/favourites.txt",
    "/mnt/sdcard/MUOS/save/pico-8/favourites.txt",
    # Standard PICO-8 Linux home fallback
    "/root/.lexaloffle/pico-8/favourites.txt",
    os.path.expanduser("~/.lexaloffle/pico-8/favourites.txt"),
]

APP_DIR    = os.path.dirname(os.path.abspath(__file__))
CFG_PATH   = os.path.join(APP_DIR, "config.txt")

def cfg_load():
    """Returns path_or_None."""
    if os.path.exists(CFG_PATH):
        lines = open(CFG_PATH).read().splitlines()
        path = lines[0].strip() if lines else ""
        if path and os.path.exists(path):
            return path
    return None

def cfg_save(path):
    with open(CFG_PATH,"w") as f:
        f.write(path + "\n")

def favs_find():
    p = cfg_load()
    if p:
        return p
    for p in SEARCH_PATHS:
        if os.path.exists(p):
            return p
    return None

def parse_entry(raw):
    line = raw.rstrip("\n")
    if not line.startswith("|"):
        return None
    parts = line.split("|")
    if len(parts) < 6:
        return None
    base = parts[2].strip()   # base slug / cart ID — used as BBS pid
    return {
        "raw":    line,
        "slug":   parts[1].strip(),
        "base":   base,
        "author": parts[4].strip(),
        "title":  parts[6].strip() if len(parts) > 6 else base,
    }

def parse_file(path):
    sections, cat_order, unsorted, current = {}, [], [], None
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if DIVIDER_RE.match(line):
            i += 1
            while i < len(lines):
                ln = lines[i].rstrip("\n")
                if DIVIDER_RE.match(ln):
                    i += 1; continue
                m = CAT_RE.match(ln)
                if m:
                    cat = m.group(1).strip()
                    if cat not in sections:
                        sections[cat] = []; cat_order.append(cat)
                    current = cat; i += 1
                break
            continue
        if line.startswith("#") or not line.strip():
            i += 1; continue
        e = parse_entry(line)
        if e:
            (sections[current] if current else unsorted).append(e)
        i += 1
    return sections, cat_order, unsorted

def write_file(path, categories, sections, unsorted):
    # FIX(bug4): rotate timestamped backups — keep only last 3 so the SD
    # card is not silently filled after many saves.
    ts_bak = path + ".bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, ts_bak)
    bak_dir  = os.path.dirname(os.path.abspath(path))
    bak_base = os.path.basename(path) + ".bak_"
    existing = sorted(
        f for f in os.listdir(bak_dir) if f.startswith(bak_base)
    )
    while len(existing) > 3:
        try:
            os.remove(os.path.join(bak_dir, existing.pop(0)))
        except OSError:
            pass

    out = []
    # FIX(unsorted-header): unsorted entries must be written FIRST with no
    # section header so PICO-8 Splore treats them as unorganised entries, not
    # as a named category called "UNSORTED".  The old code wrote them last
    # under a "# UNSORTED" wrapper which made Splore show an extra category.
    remaining = list(unsorted) + sections.get("UNSORTED",[])
    if remaining:
        out += [e["raw"] for e in remaining]
        out.append("")
    for cat in categories:
        if cat == "UNSORTED":
            continue
        entries = sections.get(cat, [])
        # Always write the header so empty categories survive a save/reload cycle
        out += ["# " + "="*60, f"# {cat}", "# " + "="*60, ""]
        if entries:
            out += [e["raw"] for e in entries]
        out.append("")
    # FIX(bug5): write to a sibling temp file then atomically rename — a
    # power-loss mid-write cannot corrupt the primary file.
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as _wf:
        _wf.write("\n".join(out))
    os.replace(tmp, path)
    return ts_bak
# =============================================================================
# Virtual keyboard  (grid, controller-navigable)
# =============================================================================

KB_ROWS = [
    list("1234567890"),
    list("qwertyuiop"),
    list("asdfghjkl-"),
    list("zxcvbnm_./"),
    ["SPACE","BKSP","DONE","CANCEL"],
]

class VKeyboard:
    def __init__(self, prompt="", initial=""):
        self.prompt    = prompt
        self.text      = initial
        self.row = self.col = 0
        self.done = self.cancelled = False

    def handle(self, btn):
        row = KB_ROWS[self.row]
        if btn=="UP":
            self.row=(self.row-1)%len(KB_ROWS)
            self.col=min(self.col,len(KB_ROWS[self.row])-1)
        elif btn=="DOWN":
            self.row=(self.row+1)%len(KB_ROWS)
            self.col=min(self.col,len(KB_ROWS[self.row])-1)
        elif btn=="LEFT":
            self.col=(self.col-1)%len(row)
        elif btn=="RIGHT":
            self.col=(self.col+1)%len(row)
        elif btn=="A":
            key=KB_ROWS[self.row][self.col]
            if key=="BKSP":      self.text=self.text[:-1]
            elif key=="DONE":    self.done=True
            elif key=="CANCEL":  self.cancelled=True
            elif key=="SPACE":
                if len(self.text)<60: self.text+=" "
            else:
                if len(self.text)<60: self.text+=key
        elif btn=="B":
            self.cancelled=True

    def draw(self, r):
        # semi-transparent overlay
        r.fill(0,0,SW,SH,(0,0,0,160))
        bx,by = _sx(30),_sy(130)
        bw,bh = min(_sx(660), SW-_sx(60)), _sy(440)
        r.fill(bx,by,bw,bh,PANEL)
        r.box(bx,by,bw,bh,ACCENT)
        r.text(self.prompt, bx+_sx(12), by+_sy(10), ACCENT, r.fbd)
        # text field
        r.fill(bx+_sx(10),by+_sy(48),bw-_sx(20),_sy(34),BG)
        r.box(bx+_sx(10),by+_sy(48),bw-_sx(20),_sy(34),DIM)
        display = (self.text or "")+"_"
        r.text_clip(display, bx+_sx(16), by+_sy(54), bw-_sx(32), WHITE, r.fmd)
        # keys
        key_h = _sy(36); key_gap = _sy(4)
        ky = by+_sy(100)
        for ri,row in enumerate(KB_ROWS):
            n    = len(row)
            kw   = min(_sx(80),(bw-_sx(20))//n-key_gap)
            totw = n*(kw+key_gap)-key_gap
            sx   = bx+(bw-totw)//2
            for ci,key in enumerate(row):
                kx   = sx+ci*(kw+key_gap)
                isel = (ri==self.row and ci==self.col)
                bg   = ACCENT if isel else (45,45,60,255)
                fg   = BG     if isel else WHITE
                r.fill(kx,ky,kw,key_h,bg)
                lbl  = key[:6]
                tw   = r.text_w(lbl.upper(),r.fsm)
                r.text(lbl.upper(), kx+(kw-tw)//2, ky+_sy(10), fg, r.fsm)
            ky += key_h + key_gap
        r.text("A=Type  B/CANCEL=Abort  DONE=Confirm",bx+_sx(12),by+bh-_sy(26),DIM,r.fsm)

# =============================================================================
# App state machine
# =============================================================================

# Screens
S_NOFILE   = "NOFILE"
S_MAIN     = "MAIN"
S_ACTION   = "ACTION"
S_CONFIRM  = "CONFIRM"
S_FILTER   = "FILTER"   # keyboard for all-entries filter
S_KEYBOARD = "KEYBOARD" # keyboard for other text input
S_AUTOSORT = "AUTOSORT" # auto-sort suggestion list
S_BBSFETCH = "BBSFETCH" # BBS fetch progress screen
S_SUGGEST  = "SUGGEST"  # suggest new categories screen
S_SGFETCH  = "SGFETCH"  # BBS fetch for suggest-categories

# Focus panels
F_LEFT  = "LEFT"
F_CATS  = "CATS"
F_RIGHT = "RIGHT"

# Context-aware hint strings
HINTS = {
    # (screen, focus, browse_mode, has_sel_entry, in_move_mode)
    # We build them dynamically in _hint_text()
}

class App:
    def __init__(self, R):
        self.R = R

        # data
        self.filepath   = None
        self.sections   = {}
        self.cat_order  = []
        self.unsorted   = []
        self.categories = list(DEFAULT_CATS)

        # ui state
        self.screen     = S_NOFILE
        self.status     = "Searching for favourites.txt…"
        self.status_ok  = True

        # left panel
        self.browse_mode  = False   # False=UNSORTED  True=ALL ENTRIES
        self.all_sort_col = 0       # 0=title 1=author 2=category
        self.all_sort_asc = True
        self.all_filter   = ""
        self._all_flat    = []      # cached [(entry, cat_name)]

        # cursors
        self.l_idx=0; self.l_scroll=0
        self.c_idx=0; self.c_scroll=0
        self.r_idx=0; self.r_scroll=0
        self.focus = F_LEFT

        # selection
        self.sel_entry   = None   # {"entry":…, "source_cat":…}
        self.sel_cat     = None
        self.move_mode   = False  # True = Up/Down moves entry within cat

        # action menu
        self.act_items = []
        self.act_idx   = 0
        self._last_sort_col = -1   # for _cycle_all_sort

        # confirm
        self.confirm_msg = ""
        self.confirm_cb  = None

        # quit flag — set by menu "Quit" option, checked in main loop
        self.quit = False

        # keyboard
        self.kb    = None
        self._kb_cb = None

        # toast notification (timed status overlay)
        self._toast_msg   = ""
        self._toast_until = 0.0   # time.monotonic() expiry

        # marquee scroll state — reset whenever highlighted item changes
        self._mq_key      = None   # (panel, index) of currently scrolling item
        self._mq_start    = 0.0    # time.monotonic() when highlight landed

        # suggest-categories screen state
        self._sg_scope    = "unsorted"  # "unsorted" or "all"
        self._sg_cards    = []   # list of {name, entries, selected}
        self._sg_idx      = 0    # cursor in card list
        self._sg_scroll   = 0
        self._sg_tag_cache= {}   # id(entry)->(entry,[tags]) from BBS fetch
        self._sg_bbs_q    = None # queue.Queue for suggest BBS fetch
        self._sg_bbs_run  = False
        self._sg_bbs_done = 0
        self._sg_bbs_tot  = 0
        self._sg_bbs_wdog = 0.0

        # auto-sort suggestion list (S_AUTOSORT screen)
        # List of dicts: {entry, suggested_cat, source}  source="kw" or "bbs"
        self.as_suggestions  = []   # full list built before entering screen
        self.as_idx          = 0    # cursor in suggestion list
        self.as_scroll       = 0
        self.as_applied      = 0    # count applied this session

        # BBS fetch state
        self._bbs_queue      = queue.Queue()   # results from daemon thread
        self._bbs_running    = False
        self._bbs_total      = 0
        self._bbs_done       = 0
        self._bbs_watchdog   = 0.0  # time.monotonic() of last queue put

        # try auto-detect
        p = favs_find()
        if p:
            self._load(p)
        else:
            self.screen = S_NOFILE
            self.status = "favourites.txt not found — press A to enter path"
            self.status_ok = False

    # ── file ops ──────────────────────────────────────────────────────────────

    def _load(self, path):
        try:
            sec, order, uns = parse_file(path)
        except Exception as e:
            self.status="Parse error: "+str(e); self.status_ok=False; return
        # Duplicate slug detection — matches Pi version auto-remove logic.
        # First occurrence in file order wins; duplicates are silently dropped.
        # Reported in status so user knows the file was cleaned.
        # Identity-based filtering throughout — never list.remove(e), which
        # matches by value and can remove the wrong object when two entries
        # have identical field values (a genuinely duplicated raw line).
        _seen_slugs = {}
        _dup_count  = 0
        _uns_keep = []
        for e in uns:
            if e["slug"] in _seen_slugs:
                _dup_count += 1
            else:
                _seen_slugs[e["slug"]] = e
                _uns_keep.append(e)
        uns = _uns_keep
        for _cat, _ents in sec.items():
            _keep = []
            for e in _ents:
                if e["slug"] in _seen_slugs and _seen_slugs[e["slug"]] is not e:
                    _dup_count += 1
                else:
                    _seen_slugs[e["slug"]] = e
                    _keep.append(e)
            sec[_cat] = _keep

        self.filepath=path; self.sections=sec
        self.cat_order=order; self.unsorted=uns
        merged=list(order)
        for c in self.categories:
            if c not in merged: merged.append(c)
        self.categories=merged
        if "UNSORTED" not in self.sections: self.sections["UNSORTED"]=[]
        self.screen=S_MAIN
        self.l_idx=self.l_scroll=0
        self.c_idx=self.c_scroll=0
        self.r_idx=self.r_scroll=0
        self.focus=F_LEFT
        self.sel_entry=None; self.sel_cat=None
        self.browse_mode=False; self.all_filter=""
        self._rebuild_all_flat()
        cfg_save(path)
        uns_n = len(self.sections.get("UNSORTED",[]))+len(self.unsorted)
        total = sum(len(v) for v in self.sections.values())+len(self.unsorted)
        dup_s = f"  |  {_dup_count} duplicates removed" if _dup_count else ""
        self.status=f"{os.path.basename(path)}  |  {uns_n} unsorted  |  {total} total{dup_s}"
        self.status_ok=True
        self.R.flush()

    def _save(self):
        if not self.filepath:
            self.status="No file loaded."; self.status_ok=False; return
        try:
            bak=write_file(self.filepath,self.categories,self.sections,self.unsorted)
            self.status=f"Saved ✓  backup: {os.path.basename(bak)}"
            self.status_ok=True
        except Exception as e:
            self.status="Save failed: "+str(e); self.status_ok=False
        self.R.flush()

    # ── all-entries flat list ─────────────────────────────────────────────────

    def _rebuild_all_flat(self):
        flat=[]
        for cat,entries in self.sections.items():
            if cat=="UNSORTED": continue
            for e in entries: flat.append((e,cat))
        for e in self.unsorted+self.sections.get("UNSORTED",[]):
            flat.append((e,"— unsorted —"))
        q=self.all_filter.lower()
        if q:
            flat=[(e,c) for (e,c) in flat
                  if q in e["title"].lower()
                  or q in e["author"].lower()
                  or q in c.lower()]
        col,rev=self.all_sort_col,not self.all_sort_asc
        if col==0:   flat.sort(key=lambda x:x[0]["title"].lower(),  reverse=rev)
        elif col==1: flat.sort(key=lambda x:x[0]["author"].lower(), reverse=rev)
        else:        flat.sort(key=lambda x:x[1].lower(),           reverse=rev)
        self._all_flat=flat
        # FIX(bounds-r_idx): clamp all cursors after every rebuild so a stale
        # index can never point past the end of a now-shorter list (e.g. after
        # applying or clearing a filter, or after removing an entry).
        le_n = len(self._left_entries())
        self.l_idx   = max(0, min(self.l_idx,   le_n - 1)) if le_n else 0
        cat_n = len(self.categories)
        self.c_idx   = max(0, min(self.c_idx,   cat_n - 1)) if cat_n else 0
        re_n = len(self._right_entries())
        self.r_idx   = max(0, min(self.r_idx,   re_n - 1)) if re_n else 0

    def _cycle_all_sort(self):
        old_col = self.all_sort_col
        if old_col == self._last_sort_col:
            self.all_sort_asc = not self.all_sort_asc
        else:
            self.all_sort_col = (old_col + 1) % 3
            self.all_sort_asc = True
        self._last_sort_col = self.all_sort_col
        self.l_idx=0; self.l_scroll=0
        self._rebuild_all_flat()
        names=["Name","Author","Category"]
        d="▲" if self.all_sort_asc else "▼"
        self.status=f"ALL ENTRIES sorted by {names[self.all_sort_col]} {d}"
        self.status_ok=True

    # ── left list entries ─────────────────────────────────────────────────────

    def _left_entries(self):
        if self.browse_mode:
            return self._all_flat   # list of (entry, cat)
        return self.sections.get("UNSORTED",[])+self.unsorted

    def _left_entry_at(self, idx):
        le=self._left_entries()
        if idx>=len(le): return None,None
        if self.browse_mode:
            e,c=le[idx]
            return e,(None if c=="— unsorted —" else c)
        return le[idx],None

    # ── right list ────────────────────────────────────────────────────────────

    def _right_entries(self):
        return self.sections.get(self.sel_cat,[]) if self.sel_cat else []

    # ── scrolling ─────────────────────────────────────────────────────────────

    def _scroll(self, panel, idx):
        # FIX(scroll-shrink): if the whole list fits in the viewport, always
        # reset the offset to 0.  Without this guard a stale scroll offset from
        # a previously long list would leave the panel showing a blank area
        # after a filter or category switch reduces the item count.
        # FIX(browse-scroll): left panel uses VISIBLE_BROWSE (10) in browse mode
        # because row_h=54 only fits ~10 rows, not the normal VISIBLE=13.
        # Using the wrong value let the cursor sit on rows 11-13 which are
        # never drawn, making the highlight disappear off-screen.
        if panel=="l":
            vis=VISIBLE_BROWSE if self.browse_mode else VISIBLE
            n=len(self._left_entries())
            if n<=vis: self.l_scroll=0; return
            if idx<self.l_scroll: self.l_scroll=idx
            elif idx>=self.l_scroll+vis: self.l_scroll=idx-vis+1
        elif panel=="c":
            n=len(self.categories)
            if n<=VISIBLE: self.c_scroll=0; return
            if idx<self.c_scroll: self.c_scroll=idx
            elif idx>=self.c_scroll+VISIBLE: self.c_scroll=idx-VISIBLE+1
        elif panel=="r":
            n=len(self._right_entries())
            if n<=VISIBLE: self.r_scroll=0; return
            if idx<self.r_scroll: self.r_scroll=idx
            elif idx>=self.r_scroll+VISIBLE: self.r_scroll=idx-VISIBLE+1

    # ── input dispatch ────────────────────────────────────────────────────────

    def handle(self, btn):
        if self.screen==S_NOFILE:       self._h_nofile(btn)
        elif self.screen==S_MAIN:       self._h_main(btn)
        elif self.screen==S_ACTION:     self._h_action(btn)
        elif self.screen==S_CONFIRM:    self._h_confirm(btn)
        elif self.screen==S_AUTOSORT:   self._h_autosort(btn)
        elif self.screen==S_BBSFETCH:   self._h_bbsfetch(btn)
        elif self.screen==S_SUGGEST:    self._h_suggest(btn)
        elif self.screen==S_SGFETCH:    self._h_sgfetch(btn)
        elif self.screen in (S_KEYBOARD,S_FILTER):
            self._h_keyboard(btn)

    def _h_nofile(self, btn):
        if btn=="A":
            self.kb=VKeyboard("Path to favourites.txt:", SEARCH_PATHS[0])
            self._kb_cb=lambda p: self._load(p)
            self.screen=S_KEYBOARD

    def _h_keyboard(self, btn):
        self.kb.handle(btn)
        if self.kb.done:
            txt=self.kb.text.strip()
            cb=self._kb_cb
            self.kb=None; self._kb_cb=None
            if self.screen==S_FILTER:
                self.all_filter=txt
                self._rebuild_all_flat()
                total=sum(len(v) for v in self.sections.values())+len(self.unsorted)
                shown=len(self._all_flat)
                self.status=f"Filter '{txt}': {shown}/{total}" if txt else f"{total} entries"
                self.status_ok=True
            else:
                if txt and cb: cb(txt)
            self.screen=S_MAIN if self.filepath else S_NOFILE
        elif self.kb.cancelled:
            self.kb=None; self._kb_cb=None
            self.screen=S_MAIN if self.filepath else S_NOFILE

    def _h_main(self, btn):
        # Panel switching
        if btn=="LEFT":
            if self.focus==F_RIGHT: self.focus=F_CATS
            elif self.focus==F_CATS: self.focus=F_LEFT
            self._mq_key=None
        elif btn=="RIGHT":
            if self.focus==F_LEFT:  self.focus=F_CATS
            elif self.focus==F_CATS and self.sel_cat: self.focus=F_RIGHT
            self._mq_key=None

        # Navigation
        elif btn in ("UP","DOWN"):
            d=-1 if btn=="UP" else 1
            if self.focus==F_LEFT:
                le=self._left_entries()
                if le:
                    # FIX(wrap): wrap instead of clamp so pressing UP at the
                    # top jumps to the bottom — feels natural on a handheld d-pad.
                    self.l_idx=(self.l_idx+d) % len(le)
                    self._scroll("l",self.l_idx)
            elif self.focus==F_CATS:
                if self.categories:
                    self.c_idx=(self.c_idx+d) % len(self.categories)
                    self._scroll("c",self.c_idx)
            elif self.focus==F_RIGHT:
                re=self._right_entries()
                if re:
                    self.r_idx=(self.r_idx+d) % len(re)
                    self._scroll("r",self.r_idx)

        # L1/R1 = page up/down on the focused panel (any panel)
        elif btn in ("L","R"):
            # FIX(BB): 'd' must be set before the focus branches — the F_RIGHT
            # branch used 'd' but it was only defined inside F_LEFT's sub-block,
            # causing NameError crash whenever L1/R1 was pressed on the right panel.
            page=VISIBLE_BROWSE if self.browse_mode else VISIBLE
            d=-page if btn=="L" else page
            if self.focus==F_LEFT:
                le=self._left_entries()
                if le:
                    self.l_idx=max(0,min(len(le)-1,self.l_idx+d))
                    self._scroll("l",self.l_idx)
            elif self.focus==F_CATS:
                self.c_idx=max(0,min(len(self.categories)-1,self.c_idx+d))
                self._scroll("c",self.c_idx)
            elif self.focus==F_RIGHT:
                re=self._right_entries()
                if re:
                    self.r_idx=max(0,min(len(re)-1,self.r_idx+d))
                    self._scroll("r",self.r_idx)

        # L2/R2 = move entry in right panel OR move category in cats column
        elif btn in ("L2","R2"):
            if self.focus==F_CATS:
                self._move_cat(-1 if btn=="L2" else 1)
            elif self.focus==F_RIGHT:
                self._move_in_cat(-1 if btn=="L2" else 1)

        # Confirm / select
        elif btn=="A":
            self._confirm()

        # Clear selection / deselect
        elif btn=="B":
            if self.sel_entry:
                self.sel_entry=None
                self.move_mode=False
                self.status="Selection cleared."; self.status_ok=True
            elif self.focus==F_RIGHT:
                self.focus=F_CATS

        # Action menu
        elif btn=="X":
            self._open_action()

        # Y = toggle browse / cycle sort / sort cat
        elif btn=="Y":
            if self.focus==F_LEFT:
                if self.browse_mode:
                    self._cycle_all_sort()
                else:
                    self._toggle_browse()
            elif self.focus==F_CATS:
                self._toggle_browse()
            elif self.focus==F_RIGHT:
                self._sort_cat()

        # START = quick save
        elif btn=="START":
            self._save()

    def _confirm(self):
        if self.focus==F_LEFT:
            le=self._left_entries()
            if not le: return
            e,src=self._left_entry_at(self.l_idx)
            if e is None: return
            self.sel_entry={"entry":e,"source_cat":src}
            self.status=f"Selected: {e['title'][:42]}  →  pick a category"
            self.status_ok=True

        elif self.focus==F_CATS:
            if not self.categories: return
            cat=self.categories[self.c_idx]
            if self.sel_entry:
                self._assign(cat)
            else:
                self.sel_cat=cat
                self.focus=F_RIGHT
                self.r_idx=0; self.r_scroll=0
                self.status=f"Viewing: {cat} ({len(self.sections.get(cat,[]))} entries)"
                self.status_ok=True

        elif self.focus==F_RIGHT:
            re=self._right_entries()
            if not re: return
            e=re[self.r_idx]
            self.sel_entry={"entry":e,"source_cat":self.sel_cat}
            self.status=f"Selected: {e['title'][:38]}  →  pick cat or L/R to reorder"
            self.status_ok=True

    def _assign(self, target_cat):
        if not self.sel_entry: return
        e=self.sel_entry["entry"]; src=self.sel_entry["source_cat"]
        if src==target_cat:
            self.sel_entry=None; return
        # remove from source — use identity (is) not equality to handle duplicate entries
        def _remove_by_id(lst):
            for i,item in enumerate(lst):
                if item is e:
                    lst.pop(i); return True
            return False
        if src is None:
            if not _remove_by_id(self.unsorted):
                _remove_by_id(self.sections.get("UNSORTED",[]))
        else:
            _remove_by_id(self.sections.get(src,[]))
        # Duplicate check — warn if same slug already in target
        if target_cat not in self.sections: self.sections[target_cat]=[]
        existing_slugs = {x["slug"] for x in self.sections[target_cat]}
        if e["slug"] in existing_slugs:
            # Ask user rather than silently deduplicating (Pi version deduped silently)
            self.confirm_msg = (f"'{ e['title'][:34]}' may already be in '{target_cat}'. Move anyway?")
            def _do_move(entry=e, tcat=target_cat, src=src):
                self.sections[tcat].append(entry)
                self.sel_entry=None
                self._rebuild_all_flat()
                self.status=f"Moved '{entry['title'][:36]}' → {tcat} (duplicate warning)"
                self.status_ok=True
                self.R.flush()
            self.confirm_cb=_do_move; self.screen=S_CONFIRM
            return
        self.sections[target_cat].append(e)
        self.sel_entry=None; self.move_mode=False
        self._rebuild_all_flat()
        self.status=f"Moved '{e['title'][:36]}' → {target_cat}"; self.status_ok=True
        self.R.flush()

    def _move_cat(self, delta):
        """Move the highlighted category up or down in self.categories."""
        n = len(self.categories)
        if n < 2: return
        idx = self.c_idx
        ni = idx + delta
        if 0 <= ni < n:
            self.categories[idx], self.categories[ni] = self.categories[ni], self.categories[idx]
            self.c_idx = ni
            self._scroll("c", ni)
            self.status = f"Category '{self.categories[ni]}' moved {'up' if delta < 0 else 'down'}"
            self.status_ok = True

    def _move_in_cat(self, delta):
        if not self.sel_entry: return
        e=self.sel_entry.get("entry")
        lst=self._right_entries()
        if not lst: return
        # find by identity, not equality
        idx=next((i for i,item in enumerate(lst) if item is e), None)
        if idx is None: return
        ni=idx+delta
        if 0<=ni<len(lst):
            lst[idx],lst[ni]=lst[ni],lst[idx]
            self.r_idx=ni
            self._scroll("r",ni)
            self.status=f"Moved '{e['title'][:36]}' {'up' if delta<0 else 'down'}"
            self.status_ok=True

    def _sort_cat(self):
        if not self.sel_cat:
            self.status="Open a category first (A on category name)"; self.status_ok=False; return
        lst=self.sections.get(self.sel_cat,[])
        lst.sort(key=lambda e:(e["author"].lower(),e["title"].lower()))
        self.sel_entry=None
        # FIX(CC): Reset cursor and scroll to top so the sorted list is visible
        # from position 0.  Without this, r_scroll stayed at the pre-sort offset
        # so the viewport showed the middle of the sorted list — making it appear
        # as if the sort had not taken effect.
        self.r_idx=0; self.r_scroll=0
        self._rebuild_all_flat()
        self.status=f"Sorted '{self.sel_cat}' A→Z by author"; self.status_ok=True
        self.R.flush()

    def _toggle_browse(self):
        self.browse_mode=not self.browse_mode
        self.sel_entry=None; self.l_idx=0; self.l_scroll=0
        self._rebuild_all_flat()
        if self.browse_mode:
            total=len(self._all_flat)
            self.status=f"ALL ENTRIES ({total} total)  |  Y=cycle sort  X=filter"
        else:
            uns=len(self.sections.get("UNSORTED",[]))+len(self.unsorted)
            self.status=f"NEW / UNSORTED ({uns} entries)  |  Y=switch to ALL ENTRIES"
        self.status_ok=True


    def _rename_category(self):
        """Rename sel_cat in-place. Opens VKeyboard pre-filled with current name."""
        if not self.sel_cat:
            self.status = "Open a category first (A on it in the middle column)."
            self.status_ok = False
            return
        old_name = self.sel_cat

        def _do_rename(new_name):
            new_name = new_name.strip().upper()
            if not new_name:
                self.status = "Rename cancelled — name was empty."; self.status_ok = False
                return
            if new_name == old_name:
                self.status = "Name unchanged."; self.status_ok = True
                return
            if new_name in self.categories:
                self.status = f"'{new_name}' already exists — rename cancelled."
                self.status_ok = False
                return
            # Update categories list
            try:
                idx = self.categories.index(old_name)
                self.categories[idx] = new_name
            except ValueError:
                pass
            # Rename sections key
            self.sections[new_name] = self.sections.pop(old_name, [])
            # Update live selection
            self.sel_cat = new_name
            self._rebuild_all_flat()
            self.status = f"Renamed '{old_name}' → '{new_name}'"
            self.status_ok = True

        self.kb = VKeyboard("Rename category (will be uppercased):", old_name)
        self._kb_cb = _do_rename
        self.screen = S_KEYBOARD

    def _delete_category(self):
        """Delete sel_cat — entries move to top of unsorted, sorted author A→Z (Pi rule)."""
        if not self.sel_cat:
            self.status = "Open a category first (A on it in the middle column)."
            self.status_ok = False
            return
        cat     = self.sel_cat
        entries = self.sections.get(cat, [])
        count   = len(entries)

        self.confirm_msg = (
            f"Delete category '{cat[:36]}'? "
            f"{count} game{'s' if count!=1 else ''} will move to Unsorted.")

        def _do_delete(c=cat, ents=list(entries)):
            # Sort displaced entries author A→Z before prepending (Pi version rule)
            sorted_ents = sorted(ents, key=lambda e: e["author"].lower())
            self.unsorted = sorted_ents + self.unsorted
            # Remove from state
            self.sections.pop(c, None)
            if c in self.categories:
                self.categories.remove(c)
            # Clear selection
            self.sel_cat   = None
            self.sel_entry = None
            self.focus     = F_CATS
            self.c_idx     = max(0, min(self.c_idx, len(self.categories)-1))
            self._rebuild_all_flat()
            self.status = (
                f"Deleted '{c}' — "
                f"{len(ents)} game{'s' if len(ents)!=1 else ''} moved to Unsorted")
            self.status_ok = True

        self.confirm_cb = _do_delete
        self.screen     = S_CONFIRM

    # ── action menu ───────────────────────────────────────────────────────────

    def _open_action(self):
        items=["Save file","Add category","Delete game","Filter all entries",
               "Clear filter","Auto-sort unsorted","Fetch BBS tags",
               "Suggest new categories"]
        # Context: category-specific items when a category is open
        if self.sel_cat:
            items += ["Rename category","Delete category"]
        items += ["Change file path","Quit","Cancel"]
        self.act_items=items; self.act_idx=0; self.screen=S_ACTION

    def _h_action(self, btn):
        if btn=="UP":   self.act_idx=(self.act_idx-1)%len(self.act_items)
        elif btn=="DOWN": self.act_idx=(self.act_idx+1)%len(self.act_items)
        elif btn in ("A","RIGHT"): self._do_action(self.act_items[self.act_idx])
        elif btn in ("B","X"):     self.screen=S_MAIN

    def _do_action(self, action):
        self.screen=S_MAIN
        if action=="Save file":
            self._save()
        elif action=="Add category":
            self.kb=VKeyboard("New category name (will be uppercased):","")
            def _add(name):
                name=name.strip().upper()
                if name and name not in self.categories:
                    self.categories.append(name); self.sections[name]=[]
                    self.status=f"Category added: {name}"; self.status_ok=True
            self._kb_cb=_add; self.screen=S_KEYBOARD
        elif action=="Delete game":
            if self.focus==F_RIGHT:
                re=self._right_entries()
                if re and self.r_idx<len(re):
                    e=re[self.r_idx]
                    self.confirm_msg=f"Delete '{e['title'][:38]}' from '{self.sel_cat}' permanently?"
                    def _rm():
                        re2=self._right_entries()
                        if re2 and self.r_idx<len(re2):
                            re2.pop(self.r_idx)
                            self.r_idx=max(0,self.r_idx-1)
                            self.sel_entry=None   # clear ghost selection
                            self._rebuild_all_flat()
                            self.status="Game deleted."; self.status_ok=True
                            self.R.flush()
                    self.confirm_cb=_rm; self.screen=S_CONFIRM
                else:
                    self.status="No game selected in right panel."; self.status_ok=False
            else:
                self.status="Focus the right panel and select a game first."; self.status_ok=False
        elif action=="Filter all entries":
            self.browse_mode=True; self._rebuild_all_flat()
            self.kb=VKeyboard("Filter (title / author / category):", self.all_filter)
            self._kb_cb=None; self.screen=S_FILTER
        elif action=="Clear filter":
            self.all_filter=""; self._rebuild_all_flat()
            self.status="Filter cleared."; self.status_ok=True
        elif action=="Auto-sort unsorted":
            self._start_autosort(use_bbs=False)
        elif action=="Fetch BBS tags":
            self._start_autosort(use_bbs=True)
        elif action=="Suggest new categories":
            self._start_suggest()
        elif action=="Rename category":
            self._rename_category()
        elif action=="Delete category":
            self._delete_category()
        elif action=="Change file path":
            self.kb=VKeyboard("Path to favourites.txt:", self.filepath or "")
            self._kb_cb=lambda p: self._load(p); self.screen=S_KEYBOARD
        elif action=="Quit":
            self.quit = True
        # Cancel does nothing

    def _h_confirm(self, btn):
        if btn=="A":
            if self.confirm_cb: self.confirm_cb()
            self.confirm_cb=None; self.screen=S_MAIN
        elif btn in ("B","X"):
            self.confirm_cb=None; self.screen=S_MAIN

    # ── hint text (context-aware) ─────────────────────────────────────────────


    # ── auto-sort + BBS fetch ─────────────────────────────────────────────────

    def _get_unsorted_pool(self):
        """All unsorted entries (plain unsorted list + any UNSORTED section)."""
        pool = list(self.unsorted)
        pool += self.sections.get("UNSORTED", [])
        return pool

    def _start_autosort(self, use_bbs=False):
        """Build keyword suggestions instantly, then optionally launch BBS fetch."""
        pool = self._get_unsorted_pool()
        if not pool:
            self.status = "No unsorted entries to suggest for."
            self.status_ok = False
            return

        # Build keyword suggestions
        self.as_suggestions = []
        for e in pool:
            cat = auto_suggest_category(e, self.categories)
            if cat:
                self.as_suggestions.append({"entry": e, "cat": cat, "source": "kw"})

        self.as_idx = 0
        self.as_scroll = 0
        self.as_applied = 0

        if not use_bbs:
            if not self.as_suggestions:
                self.status = "No keyword matches found in unsorted entries."
                self.status_ok = False
                return
            self.screen = S_AUTOSORT
            n = len(self.as_suggestions)
            self.status = f"Auto-sort: {n} suggestion{'s' if n!=1 else ''} — A=Apply  B=Skip  X=Apply all  START=Done"
            self.status_ok = True
        else:
            # Pre-flight: read WiFi operstate from sysfs — instant, non-blocking
            ok, reason = check_network()
            if not ok:
                self._toast(reason, duration=5.0)
                if self.as_suggestions:
                    self.screen = S_AUTOSORT
                    n = len(self.as_suggestions)
                    self.status = f"Offline — showing {n} keyword suggestion{'s' if n!=1 else ''} only"
                    self.status_ok = True
                else:
                    self.status = reason
                    self.status_ok = False
                return
            # Network is up — launch BBS fetch thread
            self._bbs_queue     = queue.Queue()
            self._bbs_running   = True
            self._bbs_total     = len(pool)
            self._bbs_done      = 0
            self._bbs_watchdog  = time.monotonic()
            self.screen         = S_BBSFETCH
            self.status         = f"Fetching BBS tags for {self._bbs_total} entries... B=Cancel"
            self.status_ok      = True

            def _worker():
                from concurrent.futures import ThreadPoolExecutor, as_completed
                with ThreadPoolExecutor(max_workers=3) as ex:
                    futures = {ex.submit(fetch_bbs_tags, e["base"]): e for e in pool}
                    for fut in as_completed(futures):
                        entry = futures[fut]
                        try:
                            tags = fut.result()
                        except Exception:
                            tags = []
                        self._bbs_queue.put(("result", entry, tags))
                self._bbs_queue.put(("done", None, None))

            threading.Thread(target=_worker, daemon=True).start()

    def _drain_bbs_queue(self):
        """Drain BBS result queue — called every frame while S_BBSFETCH active.
        Handles screen transition directly when fetch completes or times out,
        so the auto-transition works regardless of whether a button was pressed.
        """
        if not self._bbs_running:
            return

        # Scaled watchdog: max(30, total*2+10)s — matches Pi version
        _wdog_limit = max(30.0, self._bbs_total * 2 + 10.0)
        if time.monotonic() - self._bbs_watchdog > _wdog_limit:
            self._bbs_running = False
            self.status = f"BBS fetch timed out — {len(self.as_suggestions)} suggestions kept"
            self.status_ok = False
            self._bbs_finish()
            return

        drained = 0
        while drained < 20:   # cap per-frame work
            try:
                kind, entry, tags = self._bbs_queue.get_nowait()
            except queue.Empty:
                break
            self._bbs_watchdog = time.monotonic()
            drained += 1
            if kind == "done":
                self._bbs_running = False
                n = len(self.as_suggestions)
                self.status = f"BBS fetch complete — {n} suggestion{'s' if n!=1 else ''} — A=Apply  B=Skip  X=Apply all"
                self.status_ok = True
                self._bbs_finish()
                return
            elif kind == "result":
                self._bbs_done += 1
                if tags:
                    cat = bbs_tags_to_category(tags, self.categories)
                    if cat:
                        # BBS result overrides keyword result for same entry
                        eid = id(entry)
                        for sug in self.as_suggestions:
                            if id(sug["entry"]) == eid:
                                sug["cat"] = cat
                                sug["source"] = "bbs"
                                break
                        else:
                            self.as_suggestions.append(
                                {"entry": entry, "cat": cat, "source": "bbs"})

    def _bbs_finish(self):
        """Transition out of S_BBSFETCH — called by drain on completion/timeout."""
        if self.as_suggestions:
            self.screen = S_AUTOSORT
        elif self._bbs_done == 0:
            # No results fetched at all — likely no network
            self.screen = S_MAIN
            self._toast("No results — check WiFi and try again", duration=5.0)
            self.status = "BBS fetch returned no tags — is WiFi connected?"
            self.status_ok = False
        else:
            self.screen = S_MAIN
            self.status = "No BBS tag or keyword matches found."
            self.status_ok = False

    def _h_bbsfetch(self, btn):
        """Handler for BBS fetch progress screen.
        Screen auto-transition is handled by _drain_bbs_queue() (called from draw).
        This handler only needs to catch B (cancel) and START (force finish).
        SELECT is handled at the main loop level (sets running=False directly).
        """
        if btn == "B":
            self._bbs_running = False
            n = len(self.as_suggestions)
            if n:
                self.screen = S_AUTOSORT
                self.status = f"Fetch cancelled — {n} suggestion{'s' if n!=1 else ''} kept"
                self.status_ok = True
            else:
                self.screen = S_MAIN
                self.status = "BBS fetch cancelled — no suggestions."
                self.status_ok = False

    def _h_autosort(self, btn):
        """Handler for auto-sort suggestion list."""
        n = len(self.as_suggestions)
        if n == 0:
            self.screen = S_MAIN
            return

        if btn == "UP":
            self.as_idx = (self.as_idx - 1) % n
            self._as_scroll()
        elif btn == "DOWN":
            self.as_idx = (self.as_idx + 1) % n
            self._as_scroll()
        elif btn == "L":
            page = max(4, (SH - _sy(110) - _sy(40)) // max(1, _sy(54)))
            self.as_idx = max(0, self.as_idx - page)
            self._as_scroll()
        elif btn == "R":
            page = max(4, (SH - _sy(110) - _sy(40)) // max(1, _sy(54)))
            self.as_idx = min(n - 1, self.as_idx + page)
            self._as_scroll()
        elif btn == "A":
            self._as_apply_one()
        elif btn == "B":
            self._as_skip_one()
        elif btn == "X":
            self._as_apply_all()
        elif btn == "START":
            # Done — go back to main, report count
            self.screen = S_MAIN
            self.status = f"Auto-sort done — {self.as_applied} game{'s' if self.as_applied!=1 else ''} assigned."
            self.status_ok = True
        elif btn == "SELECT":
            self.quit = True

    def _as_scroll(self):
        # Match vis to _draw_autosort exactly so scroll and render stay in sync
        bh  = SH - _sy(110)
        vis = max(4, (bh - _sy(40)) // max(1, _sy(54)))
        if self.as_idx < self.as_scroll:
            self.as_scroll = self.as_idx
        elif self.as_idx >= self.as_scroll + vis:
            self.as_scroll = self.as_idx - vis + 1

    def _as_apply_one(self):
        if not self.as_suggestions:
            return
        sug = self.as_suggestions[self.as_idx]
        e   = sug["entry"]
        cat = sug["cat"]
        # Remove from unsorted pool
        for lst in (self.unsorted, self.sections.get("UNSORTED", [])):
            for i, item in enumerate(lst):
                if item is e:
                    lst.pop(i)
                    break
        # Add to category
        self.sections.setdefault(cat, []).append(e)
        self.as_applied += 1
        # Remove from suggestion list
        self.as_suggestions.pop(self.as_idx)
        if self.as_idx >= len(self.as_suggestions) and self.as_idx > 0:
            self.as_idx -= 1
        self._as_scroll()
        self.sel_entry = None
        self._rebuild_all_flat()
        if not self.as_suggestions:
            self.screen = S_MAIN
            self.status = f"Auto-sort done — {self.as_applied} game{'s' if self.as_applied!=1 else ''} assigned."
            self.status_ok = True

    def _as_skip_one(self):
        if not self.as_suggestions:
            self.screen = S_MAIN
            return
        self.as_suggestions.pop(self.as_idx)
        if self.as_idx >= len(self.as_suggestions) and self.as_idx > 0:
            self.as_idx -= 1
        self._as_scroll()
        if not self.as_suggestions:
            self.screen = S_MAIN
            self.status = f"Auto-sort done — {self.as_applied} game{'s' if self.as_applied!=1 else ''} assigned."
            self.status_ok = True

    def _as_apply_all(self):
        count = 0
        for sug in list(self.as_suggestions):
            e   = sug["entry"]
            cat = sug["cat"]
            for lst in (self.unsorted, self.sections.get("UNSORTED", [])):
                for i, item in enumerate(lst):
                    if item is e:
                        lst.pop(i)
                        break
            self.sections.setdefault(cat, []).append(e)
            count += 1
        self.as_suggestions = []
        self.as_applied += count
        self.sel_entry = None
        self._rebuild_all_flat()
        self.screen = S_MAIN
        self.status = f"Applied all — {self.as_applied} game{'s' if self.as_applied!=1 else ''} assigned. Don't forget to Save!"
        self.status_ok = True

    # ── draw: BBS fetch progress ──────────────────────────────────────────────

    def _draw_bbsfetch(self):
        R = self.R
        bw,bh = _sx(400),_sy(180)
        bx,by = (SW-bw)//2, (SH-bh)//2
        R.fill(bx, by, bw, bh, PANEL)
        R.box(bx, by, bw, bh, ACCENT)
        R.text("Fetching BBS Tags", bx+_sx(18), by+_sy(16), YELLOW, R.fbg)
        R.text("Connecting to lexaloffle.com...", bx+_sx(18), by+_sy(50), WHITE, R.fmd)
        done  = self._bbs_done
        total = self._bbs_total
        pct   = int(100 * done / total) if total else 0
        bar_w = bw - _sx(40)
        bar_x = bx + _sx(20)
        bar_y = by + _sy(90)
        R.fill(bar_x, bar_y, bar_w, _sy(20), BG)
        R.fill(bar_x, bar_y, int(bar_w * done / max(total,1)), _sy(20), ACCENT)
        R.box(bar_x, bar_y, bar_w, _sy(20), DIM)
        R.text(f"{done} / {total}  ({pct}%)", bar_x, bar_y+_sy(28), DIM, R.fsm)
        found = len(self.as_suggestions)
        R.text(f"{found} suggestion{'s' if found!=1 else ''} found so far", bx+_sx(18), by+_sy(130), TEAL, R.fsm)
        R.text("B = Cancel and keep partial results", bx+_sx(18), by+_sy(150), DIM, R.fsm)

    # ── draw: auto-sort suggestion list ──────────────────────────────────────

    def _draw_autosort(self):
        R = self.R
        n   = len(self.as_suggestions)
        bx, by = _sx(20), _sy(50)
        bw, bh = SW - _sx(40), SH - _sy(110)
        R.fill(bx, by, bw, bh, PANEL)
        R.box(bx, by, bw, bh, ACCENT)
        R.text("Auto-Sort Suggestions", bx + _sx(10), by + _sy(8), YELLOW, R.fbg)
        R.text(f"{n} remaining", bx + bw - _sx(120), by + _sy(8), DIM, R.fsm)
        R.hline(bx, by + _sy(30), bw, DIM)

        row_h  = _sy(54)
        vis    = max(4, (bh - _sy(40)) // row_h)
        list_y = by + _sy(36)

        for i in range(vis):
            idx = self.as_scroll + i
            if idx >= n:
                break
            sug  = self.as_suggestions[idx]
            e    = sug["entry"]
            cat  = sug["cat"]
            src  = sug["source"]
            ry   = list_y + i * row_h
            sel  = (idx == self.as_idx)
            if sel:
                R.fill(bx + _sx(4), ry, bw - _sx(8), row_h - 2, SEL_BG)
            src_col  = TEAL if src == "bbs" else DIM
            src_lbl  = "[BBS]" if src == "bbs" else "[kw]"
            title_col = YELLOW if sel else WHITE
            R.text_clip(e["title"],   bx+_sx(10), ry+_sy(4),  bw-_sx(130), title_col, R.fbd)
            R.text(src_lbl,           bx+bw-_sx(60), ry+_sy(4), src_col, R.fsm)
            R.text_clip(e["author"],  bx+_sx(10), ry+_sy(24), bw-_sx(20), DIM, R.fsm)
            R.text_clip(f"-> {cat}", bx+_sx(10), ry+_sy(38), bw-_sx(20), TEAL, R.fsm)

        # scrollbar hint
        if n > vis:
            R.text(f"{self.as_idx+1}/{n}", bx+bw-_sx(50), by+bh-_sy(20), DIM, R.fsm)

        # hint bar
        R.fill(0, SH - 34, SW, 34, PANEL)
        R.hline(0, SH - 34, SW, DIM)
        R.text_clip("↑↓=Navigate  L1/R1=Page  A=Assign  B=Skip  X=Apply ALL  START=Done",
                    8, SH - 24, SW - 16, DIM, R.fsm)


    def _mq_offset(self, panel, idx, tw, maxw):
        """Return the current marquee scroll offset in pixels.
        tw   = full text pixel width (from R.text_w).
        maxw = available column width.
        Returns 0 when tw <= maxw (text fits, no scroll).
        Timeline: 1s pause -> scroll -> 1s pause -> reset -> repeat.
        """
        if tw <= maxw:
            return 0
        key = (panel, idx)
        if self._mq_key != key:
            self._mq_key   = key
            self._mq_start = time.monotonic()
        overflow   = tw - maxw
        speed      = 60.0          # pixels per second
        pause      = 1.0           # seconds pause at each end
        scroll_dur = overflow / speed
        cycle      = pause + scroll_dur + pause
        t = (time.monotonic() - self._mq_start) % cycle
        if t < pause:
            return 0
        elif t < pause + scroll_dur:
            return int((t - pause) * speed)
        else:
            return overflow   # hold at end during final pause

    def _toast(self, msg, duration=4.0):
        """Show a timed toast notification at the bottom of the screen."""
        self._toast_msg   = msg
        self._toast_until = time.monotonic() + duration


    # ── suggest-categories ────────────────────────────────────────────────────

    def _sg_get_pool(self):
        """Entries to scan based on current scope."""
        pool = list(self.unsorted) + self.sections.get("UNSORTED", [])
        if self._sg_scope == "all":
            for cat in self.categories:
                if cat != "UNSORTED":
                    pool.extend(self.sections.get(cat, []))
        return pool

    def _sg_build_cards(self):
        """Compute merged keyword + BBS suggestions, return sorted card list.
        Card: {name:str, entries:[entry,...], selected:bool}
        BBS wins over keyword when entry count is higher (Pi version rule).
        """
        pool = self._sg_get_pool()

        kw_sugs  = suggest_new_categories(pool, self.categories)
        # Filter tag cache to entries in the current pool only — matches Pi
        # _rebuild_cards behaviour. Without this, when scope is "unsorted" but
        # the cache was built in "all" mode, categorised entries bleed into the
        # unsorted suggestions.
        pool_ids = {id(e) for e in pool}
        filtered_cache = {eid: v for eid, v in self._sg_tag_cache.items()
                          if eid in pool_ids}
        bbs_sugs = (suggest_new_categories_from_tags(filtered_cache, self.categories)
                    if filtered_cache else {})

        merged = dict(kw_sugs)
        for cat, ents in bbs_sugs.items():
            if cat not in merged or len(ents) > len(merged[cat]):
                merged[cat] = ents

        cards = []
        for proposed, ents in sorted(merged.items()):
            cards.append({"name": proposed, "entries": ents, "selected": True})
        return cards

    def _start_suggest(self):
        """Enter S_SUGGEST screen — build keyword cards immediately."""
        self._sg_scope    = "unsorted"
        self._sg_tag_cache= {}
        self._sg_bbs_run  = False
        self._sg_bbs_done = 0
        self._sg_bbs_tot  = 0
        self._sg_bbs_q    = None
        self._sg_cards    = self._sg_build_cards()
        self._sg_idx      = 0
        self._sg_scroll   = 0
        self.screen       = S_SUGGEST
        n = len(self._sg_cards)
        if n:
            self.status = (f"{n} suggestion{'s' if n!=1 else ''} — "
                           "A=Toggle  X=Rename  Y=Scope  L2=Fetch BBS  START=Apply")
        else:
            self.status = "No suggestions found — try Y to scan All Entries or L2 for BBS tags"
        self.status_ok = True

    # ── BBS fetch for suggest (separate queue from autosort BBS) ─────────────

    def _sg_start_fetch(self):
        """Launch BBS fetch thread for suggest-categories."""
        pool = self._sg_get_pool()
        if not pool:
            self._toast("No entries to fetch tags for", duration=3.0)
            return
        self._sg_bbs_q    = queue.Queue()
        self._sg_bbs_run  = True
        self._sg_bbs_done = 0
        self._sg_bbs_tot  = len(pool)
        self._sg_bbs_wdog = time.monotonic()
        self.screen       = S_SGFETCH
        self.status       = f"Fetching BBS tags for {self._sg_bbs_tot} entries... B=Cancel"
        self.status_ok    = True

        def _worker():
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = {ex.submit(fetch_bbs_tags, e["base"]): e for e in pool}
                for fut in as_completed(futures):
                    entry = futures[fut]
                    try:
                        tags = fut.result()
                    except Exception:
                        tags = []
                    self._sg_bbs_q.put(("result", entry, tags))
            self._sg_bbs_q.put(("done", None, None))

        threading.Thread(target=_worker, daemon=True).start()

    def _sg_drain_queue(self):
        """Drain BBS fetch queue for suggest screen. Handles transition on done."""
        if not self._sg_bbs_run:
            return
        limit = max(30.0, self._sg_bbs_tot * 2 + 10.0)
        if time.monotonic() - self._sg_bbs_wdog > limit:
            self._sg_bbs_run = False
            self._toast("BBS fetch timed out — keyword results shown", duration=4.0)
            self._sg_cards = self._sg_build_cards()
            self._sg_idx = min(self._sg_idx, max(0, len(self._sg_cards)-1))
            self.screen = S_SUGGEST
            return
        drained = 0
        while drained < 20:
            try:
                kind, entry, tags = self._sg_bbs_q.get_nowait()
            except queue.Empty:
                break
            self._sg_bbs_wdog = time.monotonic()
            drained += 1
            if kind == "done":
                self._sg_bbs_run = False
                self._sg_cards = self._sg_build_cards()
                self._sg_idx = min(self._sg_idx, max(0, len(self._sg_cards)-1))
                n = len(self._sg_cards)
                self.status = (f"BBS fetch complete — {n} suggestion{'s' if n!=1 else ''} — "
                               "A=Toggle  X=Rename  START=Apply")
                self.status_ok = True
                self.screen = S_SUGGEST
                return
            elif kind == "result":
                self._sg_bbs_done += 1
                if tags:
                    self._sg_tag_cache[id(entry)] = (entry, tags)

    def _h_sgfetch(self, btn):
        """Handler for S_SGFETCH (BBS fetch for suggest screen)."""
        if btn == "B":
            self._sg_bbs_run = False
            self._sg_cards = self._sg_build_cards()
            self._sg_idx = min(self._sg_idx, max(0, len(self._sg_cards)-1))
            n = len(self._sg_cards)
            self.screen = S_SUGGEST
            self.status = (f"Fetch cancelled — {n} suggestion{'s' if n!=1 else ''} kept"
                           if n else "Fetch cancelled.")
            self.status_ok = True

    # ── suggest screen handler ────────────────────────────────────────────────

    def _sg_scroll_view(self):
        vis = max(2, (SH - _sy(120)) // _sy(72))
        if self._sg_idx < self._sg_scroll:
            self._sg_scroll = self._sg_idx
        elif self._sg_idx >= self._sg_scroll + vis:
            self._sg_scroll = self._sg_idx - vis + 1

    def _h_suggest(self, btn):
        """Handler for S_SUGGEST screen."""
        n = len(self._sg_cards)

        if btn == "UP":
            if n: self._sg_idx = (self._sg_idx - 1) % n; self._sg_scroll_view()
        elif btn == "DOWN":
            if n: self._sg_idx = (self._sg_idx + 1) % n; self._sg_scroll_view()
        elif btn == "L":
            if n:
                vis = max(2, (SH - _sy(120)) // _sy(72))
                self._sg_idx = max(0, self._sg_idx - vis); self._sg_scroll_view()
        elif btn == "R":
            if n:
                vis = max(2, (SH - _sy(120)) // _sy(72))
                self._sg_idx = min(n-1, self._sg_idx + vis); self._sg_scroll_view()
        elif btn == "A":
            # Toggle selected state of highlighted card
            if n:
                self._sg_cards[self._sg_idx]["selected"] = \
                    not self._sg_cards[self._sg_idx]["selected"]
        elif btn == "X":
            # Rename highlighted card via VKeyboard
            if n:
                card = self._sg_cards[self._sg_idx]
                def _rename_cb(new_name):
                    nn = new_name.strip().upper()
                    if nn:
                        card["name"] = nn
                self.kb = VKeyboard("Rename category:", card["name"])
                self._kb_cb = _rename_cb
                self.screen = S_KEYBOARD
        elif btn == "Y":
            # Toggle scope and rebuild
            self._sg_scope = "all" if self._sg_scope == "unsorted" else "unsorted"
            self._sg_cards = self._sg_build_cards()
            self._sg_idx = 0; self._sg_scroll = 0
            scope_lbl = "All Entries" if self._sg_scope == "all" else "Unsorted Only"
            n2 = len(self._sg_cards)
            self.status = (f"Scope: {scope_lbl} — {n2} suggestion{'s' if n2!=1 else ''}")
            self.status_ok = True
        elif btn == "L2":
            # Start BBS fetch
            self._sg_start_fetch()
        elif btn == "START":
            self._sg_apply()
        elif btn == "B":
            self.screen = S_MAIN
            self.status = "Suggest categories cancelled."
            self.status_ok = False

    def _sg_apply(self):
        """Create checked categories and move entries into them."""
        created = moved = skipped = 0
        for card in self._sg_cards:
            if not card["selected"]:
                skipped += 1
                continue
            final = card["name"].strip().upper()
            if not final:
                continue
            if final not in self.categories:
                self.categories.append(final)
                self.sections[final] = []
                created += 1
            for entry in card["entries"]:
                # Find and remove from current location (identity-based)
                for lst_name, lst in list(self.sections.items()) + [("__unsorted__", self.unsorted)]:
                    actual = self.unsorted if lst_name == "__unsorted__" else lst
                    for i, e in enumerate(actual):
                        if e is entry:
                            actual.pop(i)
                            break
                    else:
                        continue
                    break
                self.sections.setdefault(final, []).append(entry)
                moved += 1

        self._rebuild_all_flat()
        self.sel_entry = None
        self.screen    = S_MAIN
        parts = []
        if created: parts.append(f"{created} categor{'y' if created==1 else 'ies'} created")
        if moved:   parts.append(f"{moved} game{'s' if moved!=1 else ''} moved")
        if skipped: parts.append(f"{skipped} skipped")
        self.status    = " — ".join(parts) + ". Don't forget to Save!" if parts else "Nothing applied."
        self.status_ok = bool(moved or created)

    # ── draw: S_SGFETCH ───────────────────────────────────────────────────────

    def _draw_sgfetch(self):
        R = self.R
        bw, bh = _sx(400), _sy(180)
        bx, by = (SW-bw)//2, (SH-bh)//2
        R.fill(bx, by, bw, bh, PANEL)
        R.box(bx, by, bw, bh, ACCENT)
        R.text("Fetching BBS Tags", bx+_sx(18), by+_sy(16), YELLOW, R.fbg)
        R.text("(for Suggest New Categories)", bx+_sx(18), by+_sy(40), DIM, R.fsm)
        done  = self._sg_bbs_done
        total = self._sg_bbs_tot
        pct   = int(100 * done / total) if total else 0
        bar_w = bw - _sx(40)
        bar_x = bx + _sx(20)
        bar_y = by + _sy(80)
        R.fill(bar_x, bar_y, bar_w, _sy(20), BG)
        R.fill(bar_x, bar_y, int(bar_w * done / max(total,1)), _sy(20), ACCENT)
        R.box(bar_x, bar_y, bar_w, _sy(20), DIM)
        R.text(f"{done} / {total}  ({pct}%)", bar_x, bar_y+_sy(28), DIM, R.fsm)
        R.text("B = Cancel and keep partial results", bx+_sx(18), by+_sy(140), DIM, R.fsm)

    # ── draw: S_SUGGEST ───────────────────────────────────────────────────────

    def _draw_suggest(self):
        R = self.R
        cards = self._sg_cards
        n = len(cards)

        # Outer panel
        bx, by = _sx(10), _sy(48)
        bw, bh = SW - _sx(20), SH - _sy(106)
        R.fill(bx, by, bw, bh, PANEL)
        R.box(bx, by, bw, bh, ACCENT)

        # Header
        scope_tag = "ALL" if self._sg_scope == "all" else "UNSORTED"
        R.text(f"Suggest New Categories  [{scope_tag}]", bx+_sx(10), by+_sy(6), YELLOW, R.fbg)
        R.hline(bx, by+_sy(28), bw, DIM)

        if not n:
            R.text("No suggestions found.", bx+_sx(10), by+_sy(44), DIM, R.fmd)
            R.text("Y = scan All Entries   L2 = Fetch BBS tags", bx+_sx(10), by+_sy(70), TEAL, R.fsm)
        else:
            card_h = _sy(72)
            vis    = max(2, (bh - _sy(34)) // card_h)
            list_y = by + _sy(32)

            for i in range(vis):
                ci = self._sg_scroll + i
                if ci >= n:
                    break
                card = cards[ci]
                ry   = list_y + i * card_h
                sel  = (ci == self._sg_idx)
                chk  = card["selected"]

                # Row background
                if sel:
                    R.fill(bx+_sx(4), ry, bw-_sx(8), card_h-_sy(2), SEL_BG)
                R.box(bx+_sx(4), ry, bw-_sx(8), card_h-_sy(2),
                      ACCENT if sel else DIM)

                # Checkbox indicator
                chk_col = GREEN if chk else DIM
                chk_lbl = "[+]" if chk else "[ ]"
                R.text(chk_lbl, bx+_sx(10), ry+_sy(6), chk_col, R.fmd)

                # Category name (bold, marquee on selected)
                name_x   = bx + _sx(42)
                name_maxw = bw - _sx(110)
                name_col = YELLOW if sel else WHITE
                if sel:
                    tw  = R.text_w(card["name"], R.fbd)
                    off = self._mq_offset("sg", ci, tw, name_maxw)
                    R.text_marquee(card["name"], name_x, ry+_sy(6), name_maxw, off, name_col, R.fbd)
                else:
                    R.text_clip(card["name"], name_x, ry+_sy(6), name_maxw, name_col, R.fbd)

                # Entry count badge
                cnt_s = f"{len(card['entries'])} game{'s' if len(card['entries'])!=1 else ''}"
                R.text(cnt_s, bx+bw-_sx(8)-R.text_w(cnt_s,R.fsm), ry+_sy(6), TEAL, R.fsm)

                # Preview: up to 3 titles on row 2
                preview = [e["title"][:22] for e in card["entries"][:3]]
                if len(card["entries"]) > 3:
                    preview.append(f"+{len(card['entries'])-3}")
                preview_txt = "  ·  ".join(preview)
                R.text_clip(preview_txt, name_x, ry+_sy(26), bw-_sx(50), DIM, R.fsm)

                # Source badge (bbs/kw) on row 2 right
                src_tags = set()
                for eid, (_, tags) in self._sg_tag_cache.items():
                    if any(id(e)==eid for e in card["entries"]) and tags:
                        src_tags.add("bbs")
                src_lbl = "[BBS]" if "bbs" in src_tags else "[kw]"
                src_col = TEAL if "bbs" in src_tags else DIM
                R.text(src_lbl, bx+bw-_sx(8)-R.text_w(src_lbl,R.fsm),
                       ry+_sy(26), src_col, R.fsm)

            # Scrollbar hint
            if n > vis:
                R.text(f"{self._sg_idx+1}/{n}", bx+bw-_sx(50), by+bh-_sy(18), DIM, R.fsm)

        # Hint bar
        HBAR = _sy(34)
        R.fill(0, SH-HBAR, SW, HBAR, PANEL)
        R.hline(0, SH-HBAR, SW, DIM)
        R.text_clip(
            "↑↓=Navigate  A=Toggle  X=Rename  Y=Scope  L1/R1=Page  L2=BBS fetch  START=Apply  B=Cancel",
            _sx(8), SH-HBAR+_sy(10), SW-_sx(16), DIM, R.fsm)


    def _hint(self):
        sc=self.screen
        if sc==S_NOFILE:
            return "A=Enter path  SELECT=Quit"
        if sc==S_ACTION:
            return "↑↓=Move  A=Select  B/X=Close  SELECT=Quit"
        if sc==S_CONFIRM:
            return "A=Yes, confirm  B=No, cancel"
        if sc in (S_KEYBOARD,S_FILTER):
            return "D-pad=Navigate keys  A=Type  B/CANCEL=Abort  DONE=Confirm"
        if sc==S_AUTOSORT:
            return "↑↓=Navigate  L1/R1=Page  A=Assign  B=Skip  X=Apply ALL  START=Done"
        if sc==S_BBSFETCH:
            return "B=Cancel fetch and keep partial results  SELECT=Quit"
        if sc==S_SGFETCH:
            return "B=Cancel BBS fetch and keep partial  SELECT=Quit"
        if sc==S_SUGGEST:
            return "↑↓=Navigate  A=Toggle  X=Rename  Y=Scope  L2=BBS  START=Apply  B=Cancel"
        # S_MAIN — context sensitive
        f=self.focus
        has_sel=self.sel_entry is not None
        bm=self.browse_mode
        if f==F_LEFT:
            if bm:
                if has_sel:
                    return "←→=Panels  A=Confirm  B=Clear sel  X=Menu  Y=Cycle sort  START=Save"
                return "↑↓=Navigate  L1/R1=Page  A=Select  B=Clear  X=Menu  Y=Cycle sort  START=Save"
            else:
                if has_sel:
                    return "↑↓=Navigate  A=Confirm sel  B=Clear  X=Menu  Y=ALL ENTRIES  START=Save"
                return "↑↓=Navigate  L1/R1=Page  A=Select  X=Menu  Y=ALL ENTRIES  START=Save"
        elif f==F_CATS:
            if has_sel:
                return "↑↓=Move  A=Assign entry here  B=Clear sel  ←=Left panel  X=Menu  Y=Toggle view"
            return "↑↓=Move  L1/R1=Page  L2/R2=Reorder cat  A=Open cat  →=Right  ←=Left  X=Menu"
        elif f==F_RIGHT:
            if has_sel:
                return "↑↓=Navigate  L1/R1=Page  L2/R2=Move entry  A=Re-select  B=Deselect  X=Menu"
            return "↑↓=Navigate  L1/R1=Page  L2/R2=Move entry  A=Select  X=Menu  Y=Sort A→Z"
        return "D-pad=Navigate  A=Confirm  B=Back  X=Menu  Y=Toggle  START=Save  SELECT=Quit"

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        R=self.R; R.clear()
        if self.screen==S_NOFILE:
            self._draw_nofile()
        elif self.screen==S_BBSFETCH:
            self._draw_main_bg()
            self._drain_bbs_queue()
            self._draw_bbsfetch()
        elif self.screen==S_SGFETCH:
            self._draw_main_bg()
            self._sg_drain_queue()
            self._draw_sgfetch()
        elif self.screen==S_SUGGEST:
            self._draw_main_bg()
            self._draw_suggest()
        elif self.screen==S_AUTOSORT:
            self._draw_main_bg()
            self._draw_autosort()
        else:
            self._draw_main_bg()
            if self.screen==S_ACTION:   self._draw_action()
            elif self.screen==S_CONFIRM: self._draw_confirm()
            elif self.screen in (S_KEYBOARD,S_FILTER) and self.kb:
                self.kb.draw(R)
        R.present()

    def _draw_nofile(self):
        R=self.R
        R.text("PICO-8 Favourites Sorter",_sx(16),_sy(18),YELLOW,R.fbg)
        R.text("favourites.txt not found.",_sx(16),_sy(72),WHITE,R.fmd)
        R.text("Press A to enter the path manually.",_sx(16),_sy(104),DIM,R.fsm)
        R.text(f"HOME={os.environ.get('HOME','?')}",_sx(16),_sy(126),TEAL,R.fsm)
        y=_sy(156); R.text("Searched:",_sx(16),y,DIM,R.fsm); y+=_sy(20)
        for p in SEARCH_PATHS:
            R.text_clip(p,_sx(26),y,SW-_sx(32),DIM,R.fsm); y+=_sy(18)
        HBAR=_sy(34)
        R.fill(0,SH-HBAR,SW,HBAR,PANEL)
        R.text(self._hint(),_sx(8),SH-HBAR+_sy(10),DIM,R.fsm)

    def _draw_main_bg(self):
        R=self.R
        # ── title bar ────────────────────────────────────────────────────────
        TBAR = _sy(44)
        R.fill(0,0,SW,TBAR,PANEL)
        R.text("PICO-8 Favourites Sorter",_sx(8),_sy(6),YELLOW,R.fbg)

        # ── hint + status bars ────────────────────────────────────────────────
        HBAR = _sy(34)   # hint bar height
        SBAR = _sy(20)   # status text height
        sc=ACCENT if self.status_ok else RED
        R.text_clip(self.status, _sx(8), SH-HBAR-SBAR, SW-_sx(16), sc, R.fsm)

        R.fill(0,SH-HBAR,SW,HBAR,PANEL)
        R.hline(0,SH-HBAR,SW,DIM)
        R.text_clip(self._hint(),_sx(8),SH-HBAR+_sy(10),SW-_sx(16),DIM,R.fsm)

        # ── three columns (proportional split) ───────────────────────────────
        CY = TBAR + _sy(6)
        CH = SH - CY - HBAR - SBAR - _sy(6)
        LW = _sx(222); CW = _sx(242); RW = SW - LW - CW - _sx(12)
        LX = 0; CX = LW + _sx(6); RX = CX + CW + _sx(6)

        self._draw_left(LX,CY,LW,CH)
        self._draw_cats(CX,CY,CW,CH)
        self._draw_right(RX,CY,RW,CH)

        # Toast notification — drawn on top of everything, auto-expires
        if self._toast_msg and time.monotonic() < self._toast_until:
            tw = min(SW - _sx(40), R.text_w(self._toast_msg, R.fmd) + _sx(32))
            tx = (SW - tw) // 2
            ty = SH - _sy(80)
            R.fill(tx, ty, tw, _sy(36), (26, 10, 10, 255))
            R.box(tx, ty, tw, _sy(36), RED)
            R.text_clip(self._toast_msg, tx+_sx(10), ty+_sy(10), tw-_sx(20), RED, R.fmd)
        elif self._toast_msg and time.monotonic() >= self._toast_until:
            self._toast_msg = ""

    def _draw_left(self, x, y, w, h):
        R=self.R
        focused=self.focus==F_LEFT
        border=ACCENT if focused else DIM
        R.fill(x+1,y,w-2,h,PANEL)
        R.box(x+1,y,w-2,h,border)

        # mode toggle header
        bm=self.browse_mode
        mode_lbl = "[ ALL ENTRIES ]" if bm else "[ NEW/UNSORTED ]"
        mode_col  = YELLOW if bm else ACCENT
        # Mode label — full width, no competition from count badge
        R.text_clip(mode_lbl, x+_sx(6), y+_sy(5), w-_sx(10), mode_col if focused else DIM, R.fbd)

        le=self._left_entries()
        n=len(le)
        # Count + filter on second line, left-aligned under the mode label
        extra=""
        if bm and self.all_filter:
            extra=f"  filter:'{self.all_filter[:8]}'"
        cnt_lbl=f"({n}){extra}"
        R.text_clip(cnt_lbl, x+_sx(6), y+_sy(24), w-_sx(10), DIM, R.fsm)

        # Sort indicator (browse mode) — right-aligned on same line as count
        if bm:
            names=["Name","Author","Cat"]
            d="▲" if self.all_sort_asc else "▼"
            sort_lbl=f"{names[self.all_sort_col]}{d}"
            R.text(sort_lbl, x+w-_sx(6)-R.text_w(sort_lbl,R.fsm), y+_sy(24), TEAL, R.fsm)

        LIST_Y = y+_sy(44) if bm else y+_sy(38)
        row_h  = ROW_H if not bm else _sy(54)   # 3-line rows in browse mode
        vis    = max(1,(h-(LIST_Y-y))//row_h)

        for i in range(vis):
            ei=self.l_scroll+i
            if ei>=n: break
            ry=LIST_Y+i*row_h
            is_cur=(ei==self.l_idx and focused)
            # get entry
            if bm:
                e,cat=le[ei]
            else:
                e=le[ei]; cat=None
            is_sel=(self.sel_entry is not None and self.sel_entry.get("entry") is e)

            if is_cur: R.fill(x+3,ry,w-6,row_h-2,SEL_BG)
            if is_sel: R.box(x+3,ry,w-6,row_h-2,ACCENT)

            tc=YELLOW if is_sel else WHITE
            title_maxw = w-_sx(14)
            if is_cur:
                tw = R.text_w(e["title"], R.fbd)
                off = self._mq_offset("l", ei, tw, title_maxw)
                R.text_marquee(e["title"],x+_sx(7),ry+_sy(2),title_maxw,off,tc,R.fbd)
            else:
                R.text_clip(e["title"],x+_sx(7),ry+_sy(2),title_maxw,tc,R.fbd)
            R.text_clip(e["author"],x+_sx(7),ry+_sy(24),w-_sx(14),DIM,R.fsm)
            if bm and cat:
                R.text_clip(cat,x+_sx(7),ry+_sy(35),w-_sx(14),TEAL,R.fsm)

        # scrollbar
        if n>vis:
            bh2=max(16,h*vis//n)
            by2=y+(h-bh2)*self.l_scroll//max(1,n-vis)
            R.fill(x+w-5,by2,3,bh2,DIM)

    def _draw_cats(self, x, y, w, h):
        R=self.R
        focused=self.focus==F_CATS
        R.fill(x+1,y,w-2,h,PANEL)
        R.box(x+1,y,w-2,h,ACCENT if focused else DIM)
        R.text("CATEGORIES",x+_sx(6),y+_sy(6),ACCENT if focused else DIM,R.fbd)

        vis=max(1,(h-_sy(30))//ROW_H)
        n=len(self.categories)
        for i in range(vis):
            ci=self.c_scroll+i
            if ci>=n: break
            cat=self.categories[ci]
            ry=y+_sy(30)+i*ROW_H
            is_cur=(ci==self.c_idx and focused)
            is_act=(cat==self.sel_cat)
            cnt=len(self.sections.get(cat,[]))

            if is_cur:  R.fill(x+3,ry,w-6,ROW_H-2,SEL_BG)
            if is_act:  R.fill(x+3,ry,w-6,ROW_H-2,PURPLE)
            if is_cur or is_act: R.box(x+3,ry,w-6,ROW_H-2,ACCENT if is_cur else PURPLE)

            lc=WHITE if (is_cur or is_act) else DIM
            cat_maxw = w-_sx(46)
            if is_cur:
                tw = R.text_w(cat, R.fbd)
                off = self._mq_offset("c", ci, tw, cat_maxw)
                R.text_marquee(cat,x+_sx(7),ry+_sy(5),cat_maxw,off,lc,R.fbd)
            else:
                R.text_clip(cat,x+_sx(7),ry+_sy(5),cat_maxw,lc,R.fbd)
            cs=str(cnt)
            R.text(cs,x+w-_sx(6)-R.text_w(cs,R.fsm),ry+_sy(5),DIM,R.fsm)

        if n>vis:
            bh=max(16,h*vis//n)
            by=y+(h-bh)*self.c_scroll//max(1,n-vis)
            R.fill(x+w-5,by,3,bh,DIM)

    def _draw_right(self, x, y, w, h):
        R=self.R
        focused=self.focus==F_RIGHT
        R.fill(x+1,y,w-2,h,PANEL)
        R.box(x+1,y,w-2,h,ACCENT if focused else DIM)

        cat_lbl=self.sel_cat or "SELECT A CATEGORY"
        R.text_clip(cat_lbl,x+_sx(6),y+_sy(5),w-_sx(60),ACCENT if focused else DIM,R.fbd)
        re=self._right_entries()
        cnt_s=f"({len(re)})" if self.sel_cat else ""
        if cnt_s:
            R.text(cnt_s,x+w-_sx(6)-R.text_w(cnt_s,R.fsm),y+_sy(6),DIM,R.fsm)

        vis=max(1,(h-_sy(30))//ROW_H)
        n=len(re)
        for i in range(vis):
            ri=self.r_scroll+i
            if ri>=n: break
            e=re[ri]; ry=y+_sy(30)+i*ROW_H
            is_cur=(ri==self.r_idx and focused)
            is_sel=(self.sel_entry is not None and self.sel_entry.get("entry") is e)

            if is_cur: R.fill(x+3,ry,w-6,ROW_H-2,SEL_BG)
            if is_sel: R.box(x+3,ry,w-6,ROW_H-2,ACCENT)

            tc=YELLOW if is_sel else WHITE
            title_maxw = w-_sx(14)
            if is_cur:
                tw = R.text_w(e["title"], R.fbd)
                off = self._mq_offset("r", ri, tw, title_maxw)
                R.text_marquee(e["title"],x+_sx(7),ry+_sy(5),title_maxw,off,tc,R.fbd)
            else:
                R.text_clip(e["title"],x+_sx(7),ry+_sy(5),title_maxw,tc,R.fbd)
            R.text_clip(e["author"],x+_sx(7),ry+_sy(21),w-_sx(14),DIM,R.fsm)

        if n>vis:
            bh=max(16,h*vis//n)
            by=y+(h-bh)*self.r_scroll//max(1,n-vis)
            R.fill(x+w-5,by,3,bh,DIM)

    def _draw_action(self):
        R=self.R
        # FIX(menu-overflow): cap height so adding items never pushes menu off-screen.
        # FIX(menu-clip): guard the render loop so items beyond the capped box
        # boundary are not drawn outside the panel.
        item_h=_sy(48); item_sel_h=_sy(44)
        mw=_sx(400)
        mh=min(len(self.act_items)*item_h+_sy(60), SH-_sy(80))
        mx=(SW-mw)//2; my=(SH-mh)//2
        R.fill(mx,my,mw,mh,PANEL)
        R.box(mx,my,mw,mh,ACCENT)
        R.text("ACTION MENU",mx+_sx(12),my+_sy(8),ACCENT,R.fbg)
        R.hline(mx,my+_sy(32),mw,DIM)
        for i,item in enumerate(self.act_items):
            iy=my+_sy(38)+i*item_h
            if iy+item_sel_h > my+mh: break
            if i==self.act_idx:
                R.fill(mx+_sx(4),iy,mw-_sx(8),item_sel_h,SEL_BG)
                R.box(mx+_sx(4),iy,mw-_sx(8),item_sel_h,ACCENT)
            R.text(item,mx+_sx(16),iy+_sy(12),WHITE if i==self.act_idx else DIM,R.fmd)
        R.text("↑↓=Move  A=Select  B=Close",mx+_sx(12),my+mh-_sy(22),DIM,R.fsm)

    def _draw_confirm(self):
        R=self.R
        mw,mh=_sx(460),_sy(150)
        mx=(SW-mw)//2; my=(SH-mh)//2
        R.fill(mx,my,mw,mh,PANEL)
        R.box(mx,my,mw,mh,RED)
        R.text("Confirm Action",mx+_sx(12),my+_sy(10),RED,R.fbg)
        R.hline(mx,my+_sy(36),mw,DIM)
        R.text_clip(self.confirm_msg,mx+_sx(12),my+_sy(52),mw-_sx(24),WHITE,R.fmd)
        R.text("A=Yes  B=No",mx+_sx(12),my+mh-_sy(26),DIM,R.fsm)

# =============================================================================
# Main loop
# =============================================================================

def main():
    if SDL.SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK) != 0:
        sys.exit("SDL_Init failed")

    SDL.SDL_JoystickOpen.argtypes=[ctypes.c_int]
    SDL.SDL_JoystickOpen.restype=ctypes.c_void_p
    SDL.SDL_JoystickEventState.argtypes=[ctypes.c_int]
    SDL.SDL_JoystickEventState.restype=ctypes.c_int

    # Post-SDL-init resolution fallback: if muOS files were absent,
    # query the display and update SW/SH + derived layout globals.
    global SW, SH, _SX, _SY, ROW_H, VISIBLE, VISIBLE_BROWSE
    if SW == 720 and SH == 720:   # only if using fallback
        try:
            class _DM(ctypes.Structure):
                _fields_=[("format",ctypes.c_uint32),("w",ctypes.c_int),
                          ("h",ctypes.c_int),("refresh",ctypes.c_int),("driverdata",ctypes.c_void_p)]
            SDL.SDL_GetCurrentDisplayMode.argtypes=[ctypes.c_int,ctypes.POINTER(_DM)]
            SDL.SDL_GetCurrentDisplayMode.restype=ctypes.c_int
            dm=_DM()
            if SDL.SDL_GetCurrentDisplayMode(0,ctypes.byref(dm))==0 and dm.w>0 and dm.h>0:
                SW,SH=dm.w,dm.h
                _SX=SW/720.0; _SY=SH/720.0
                ROW_H=max(1,int(44*_SY))
                VISIBLE=max(5,(SH-int(110*_SY))//ROW_H)
                VISIBLE_BROWSE=max(4,(SH-int(130*_SY))//max(1,int(54*_SY)))
        except Exception:
            pass
    win=SDL.SDL_CreateWindow(b"PICO-8 Favourites Sorter",
        SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,SW,SH,0)
    rend=SDL.SDL_CreateRenderer(win,-1,2)
    if not rend:
        rend=SDL.SDL_CreateRenderer(win,-1,1)

    SDL.SDL_JoystickOpen(0)
    SDL.SDL_JoystickEventState(1)

    R=Renderer(win,rend,find_font(),find_bold_font())
    app=App(R)

    ev=Event()
    running=True
    ms=1000//FPS

    held=None; held_t=0
    DELAY=400; RATE=150
    NAV_BTNS=("UP","DOWN","LEFT","RIGHT")

    buttons_held=set()

    def fire(btn):
        _prev_screen=app.screen
        try:
            app.handle(btn)
        except Exception as _handle_err:
            import traceback
            with open("/tmp/pico8sorter_crash.log", "a") as _f:
                _f.write(f"\n--- handle() crash btn={btn} screen={app.screen} ---\n")
                traceback.print_exc(file=_f)
            app.status = f"ERROR: {_handle_err}"
            app.status_ok = False
            app.screen = S_MAIN
        nonlocal held, running
        if app.quit:
            running=False; return
        if app.screen!=_prev_screen:
            held=None

    while running:
        t0=SDL.SDL_GetTicks()

        while SDL.SDL_PollEvent(ctypes.byref(ev)):
            et=ev.type; btn=None

            if et==SDL_QUIT_EVENT:
                running=False

            elif et==SDL_KEYDOWN:
                k=ev.key.keysym.sym
                if ev.key.repeat!=0: pass
                elif k==SDLK_ESCAPE:    running=False
                elif k==SDLK_UP:        btn="UP"
                elif k==SDLK_DOWN:      btn="DOWN"
                elif k==SDLK_LEFT:      btn="LEFT"
                elif k==SDLK_RIGHT:     btn="RIGHT"
                elif k==SDLK_RETURN:    btn="A"
                elif k==SDLK_BACKSPACE: btn="B"
                elif k==SDLK_TAB:       btn="X"

            elif et==SDL_JOYBUTTONDOWN_EV:
                b=ev.cbutton.button
                buttons_held.add(b)
                if b==JOY_A:     btn="A"
                elif b==JOY_B:     btn="B"
                elif b==JOY_X:     btn="X"
                elif b==JOY_Y:     btn="Y"
                elif b==JOY_L:     btn="L"
                elif b==JOY_R:     btn="R"
                elif b==JOY_L2:    btn="L2"
                elif b==JOY_R2:    btn="R2"
                elif b==JOY_START: btn="START"
                elif b==JOY_BACK:  running=False  # SELECT = quit

            elif et==SDL_JOYBUTTONUP_EV:
                b=ev.cbutton.button
                buttons_held.discard(b)
                bup={JOY_A:"A",JOY_B:"B",JOY_X:"X",JOY_Y:"Y",
                     JOY_L:"L",JOY_R:"R"}.get(b)
                if bup and bup==held:
                    held=None

            elif et==SDL_JOYHATMOTION_EV:
                held=None   # clear before arming new direction
                hv=ev.jhat.value
                if   hv & SDL_HAT_UP:    btn="UP"
                elif hv & SDL_HAT_DOWN:  btn="DOWN"
                elif hv & SDL_HAT_LEFT:  btn="LEFT"
                elif hv & SDL_HAT_RIGHT: btn="RIGHT"

            if btn:
                fire(btn)
                if btn in NAV_BTNS:
                    held=btn; held_t=t0
                else:
                    held=None

        if held in NAV_BTNS:
            now=SDL.SDL_GetTicks()
            if now-held_t >= DELAY+RATE:
                fire(held); held_t+=RATE

        try:
            app.draw()
        except Exception as _draw_err:
            import traceback
            _log = f"/tmp/pico8sorter_crash.log"
            with open(_log, "a") as _f:
                _f.write(f"\n--- draw() crash screen={app.screen} ---\n")
                traceback.print_exc(file=_f)
            app.status = f"DRAW ERROR: {_draw_err}"
            app.status_ok = False
            app.screen = S_MAIN   # recover to main screen
        el=SDL.SDL_GetTicks()-t0
        if el<ms: SDL.SDL_Delay(ms-el)

    SDL.SDL_Quit()

if __name__=="__main__":
    main()