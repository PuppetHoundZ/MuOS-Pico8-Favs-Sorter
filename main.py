#!/usr/bin/env python3
# =============================================================================
# PICO-8 Favourites Sorter — muOS Edition  v1.7.12
# For: Anbernic RG Cube XX (720×720) running MustardOS
# Pure Python 3 + SDL2 via ctypes. No pip, no extras needed.
#
# Changelog:
#   v1.7.12 (2026-06-30) — Three changes from user feedback:
#     (1) DEFAULT_CATS reverted to original 10 (CURRENT FAVORITES through
#         CLOCKS/UTILITIES/TOYS). The 7 categories added in v1.7.x sessions
#         (SPORTS/PINBALL, SIM/TYCOON/SANDBOX, HORROR/STEALTH, RHYTHM,
#         METROIDVANIA, CARD/BOARD/STRATEGY, IDLE/CLICKER) are no longer
#         pre-seeded on every install — they now surface only via the
#         existing Suggest-New-Category screen once >= MIN_SUGGEST entries
#         cluster around that theme, same as any other new-category
#         proposal. AUTO_SORT_RULES/TAG_TO_CAT keep their entries for all
#         17 categories unchanged — the existing "cat_name not in
#         categories: skip" guard already makes a rule dormant until the
#         category is actually added, so once a suggestion is accepted the
#         matching auto-sort rule wakes up automatically with no further
#         code change needed. This also resolves the v1.7.11 naming-overlap
#         concern: KEYWORD_TO_NEW_CAT/TAG_TO_NEW_CAT renamed to the exact
#         canonical category strings (was: generic "HORROR"/"SPORTS"/
#         "CARD & BOARD GAMES"/"SIMULATION"/"IDLE & CLICKER", now matches
#         AUTO_SORT_RULES exactly), plus added RHYTHM/METROIDVANIA entries
#         that were missing from the suggestion tables entirely before.
#         TOWER DEFENCE and MULTIPLAYER remain genuine novel suggestions
#         with no dormant AUTO_SORT_RULES counterpart (no built-in category
#         covers them yet).
#     (2) New suggest_author_categories(): clusters unsorted/all-scope
#         entries by author, proposing "<AUTHOR> COLLECTION" for any author
#         with >= MIN_SUGGEST works not already covered by an existing
#         category (correctly skips authors like "mot" since MOT COLLECTION
#         already exists — verified via simulation). Wired into
#         _sg_build_cards() alongside the existing keyword/BBS theme
#         suggestions; author cards never collide with theme-card names so
#         they're simply unioned in.
#     (3) Bug found while stress-testing (1)+(2) together: _sg_apply()'s
#         entry-relocation loop appended+counted "moved" unconditionally
#         even when the identity-search failed to find the entry anywhere
#         in current state. Cross-card overlap (same entry matching both a
#         theme card and an author card) turns out to be safe — the search
#         rescans full live state each card, so an already-relocated entry
#         is still found and cleanly re-homed to whichever card is applied
#         last. But a stale entries-list reference (e.g. the entry was
#         deleted via the dupes-review screen while a Suggest-Categories
#         session was still open with old cards) would have silently
#         resurrected a "ghost" copy into the new category. Fixed: only
#         append+count as moved if the identity-search actually found and
#         removed it; otherwise count as skipped. Verified via direct stub
#         test exercising the two-card-same-entry path.
#   v1.7.11 (2026-06-30) — Genre coverage: 5 deferred categories added.
#                                 Added HORROR / STEALTH, RHYTHM,
#                                 METROIDVANIA, CARD / BOARD / STRATEGY,
#                                 and IDLE / CLICKER to DEFAULT_CATS and
#                                 AUTO_SORT_RULES, inserted right before
#                                 CLOCKS / UTILITIES / TOYS (same pattern
#                                 used for SPORTS/PINBALL and SIM/TYCOON in
#                                 an earlier session) so existing keyword
#                                 priority is unaffected — e.g. RACING's
#                                 "beat" (beat-em-up) still wins over the
#                                 new RHYTHM category, since RHYTHM
#                                 deliberately avoids "beat" as a keyword
#                                 to prevent collision. METROIDVANIA kept
#                                 narrow (just "metroidvania"/"vania") so
#                                 it doesn't steal ordinary platformer
#                                 matches via "explore" etc. Also updated
#                                 TAG_TO_CAT (used for BBS-tag-based
#                                 suggestions): "metroidvania" tag now maps
#                                 to METROIDVANIA instead of PLATFORMERS;
#                                 "horror" tag now maps to HORROR/STEALTH
#                                 instead of ATMOSPHERIC; "rhythm" tag now
#                                 maps to RHYTHM instead of MUSIC/DEMOSCENE;
#                                 added "stealth"/"dance"/"card"/"board"/
#                                 "chess"/"tabletop"/"idle"/"clicker"/
#                                 "incremental" tags. Existing categorized
#                                 entries in favourites.txt are NOT
#                                 retroactively re-sorted — this only
#                                 affects auto-suggest behavior for newly
#                                 added/uncategorized entries going forward.
#   v1.7.10 (2026-06-30) — Fix 12: missing `import time` — NameError crash.
#                                 `import time` was absent from the top-level
#                                 import line entirely, while time.monotonic()
#                                 is called in 10+ places: the marquee-scroll
#                                 helper (_mq_offset, used by ALL THREE panels
#                                 — left/cats/right — whenever the highlighted
#                                 row's text overflows its column width),
#                                 toast notifications (_toast/_draw_main_bg),
#                                 and both BBS-fetch watchdogs (regular +
#                                 suggest-categories). Reported symptom:
#                                 moving the selector into the categories
#                                 column after picking an Unsorted entry threw
#                                 "NameError: name 'time' is not defined" —
#                                 that's _mq_offset firing because the
#                                 category name overflowed the column and
#                                 became the active marquee target. Same crash
#                                 would equally hit toasts and BBS fetches.
#                                 Fixed by adding `time` to the import line.
#   v1.7.9 (2026-06-30) — Fix 11: silent boot-crash blind spot.
#                                 main()'s startup sequence (SDL_Init ->
#                                 SDL_CreateWindow -> SDL_CreateRenderer ->
#                                 Renderer() -> App()) had ZERO exception
#                                 handling and zero logging — every other
#                                 code path (fire()/draw() in the main loop)
#                                 writes failures to
#                                 /tmp/pico8sorter_crash.log, but a failure
#                                 during startup itself just died with a
#                                 Python traceback to stderr, which muOS has
#                                 nowhere to show and nowhere to save.
#                                 Extracted startup into _boot(), wrapped
#                                 end-to-end: SDL_CreateWindow/
#                                 SDL_CreateRenderer return values are now
#                                 checked and SDL_GetError() is logged before
#                                 exiting; Renderer()/App() init failures are
#                                 caught, logged with full traceback, then
#                                 re-raised. SDL_GetError's ctypes restype
#                                 set to c_char_p (was unset/default int —
#                                 truncates the pointer on 64-bit). _load()'s
#                                 try/except widened to cover
#                                 reconcile_stripped_categories() too.
#                                 NEXT TIME IT FAILS TO BOOT: check
#                                 /tmp/pico8sorter_crash.log first.
#
#   v1.7.8 (2026-06-30) — Fix 10: category-move data loss + Reload feature.
#                                 BUG FOUND (serious): _assign() removed the
#                                 entry from its source list BEFORE showing
#                                 the "may already be in target — move
#                                 anyway?" confirm dialog. Declining (B) had
#                                 no skip-callback, so the entry was simply
#                                 never re-added anywhere — gone from every
#                                 list, with no recovery short of reloading
#                                 the whole file. Reproduced with an
#                                 identity-based check (not slug equality,
#                                 since the bug specifically only manifests
#                                 when a slug-duplicate already exists in
#                                 the target, which is exactly when the
#                                 dialog appears). Fixed by capturing the
#                                 list the entry was removed from and wiring
#                                 a confirm_skip_cb that restores it there
#                                 on decline. Verified: decline restores to
#                                 source (incl. when source is a real
#                                 category, not just Unsorted), confirm
#                                 still moves it, and the ordinary no-
#                                 duplicate move path is unaffected.
#                                 NEW: "Reload file (discard changes)" in
#                                 the X menu — re-parses favourites.txt from
#                                 disk via the same _load() path as startup
#                                 (so it also re-runs Fix 6/7 strip
#                                 recovery), behind a confirm dialog.
#                                 BUG FOUND while building this: _load()'s
#                                 category-merge logic merged the file's
#                                 headers against self.categories — the
#                                 LIVE, possibly-dirty in-memory list. An
#                                 unsaved "Add category" would therefore
#                                 survive a reload, defeating the point of
#                                 "discard changes." Fixed to merge against
#                                 the fixed DEFAULT_CATS baseline instead
#                                 (also makes "Change file path" correctly
#                                 stop carrying over an old file's custom
#                                 categories into an unrelated new file).
#                                 Verified with a combined stress test:
#                                 delete an entry, manually duplicate
#                                 another, add a stray unsorted entry, add
#                                 an unsaved category, and scramble category
#                                 contents — Reload exactly restores the
#                                 last-saved-on-disk state in every respect.
#   v1.7.7 (2026-06-30) — Fix 9: category create/rename/delete safety audit.
#                                 Two real bugs found by deliberately
#                                 stress-testing category mutation against
#                                 the master-record system:
#                                 (1) Deleting or renaming a category only
#                                 updated in-memory state + favourites.txt —
#                                 the master JSON kept the OLD category
#                                 name for those slugs until the next
#                                 "Save file". If PICO-8 stripped the file
#                                 in that window, reconcile_stripped_
#                                 categories() would faithfully recover
#                                 entries into the just-deleted/renamed
#                                 category, silently undoing the user's
#                                 action. Fixed with new
#                                 set_master_category_for_entries(), called
#                                 immediately from both _rename_category and
#                                 _delete_category — delete marks the
#                                 displaced slugs cat="UNSORTED" in master
#                                 (excluded from recovery, but history kept
#                                 for the "back up every favourite ever
#                                 categorized" master-list goal); rename
#                                 re-keys them to the new name right away.
#                                 Verified: simulated delete -> immediate
#                                 PICO-8 strip -> reconcile no longer
#                                 resurrects the deleted category, entries
#                                 correctly stay unsorted.
#                                 (2) "Add category" / "Rename category"
#                                 had no guard against the name "UNSORTED" —
#                                 since self.categories normally never
#                                 contains "UNSORTED" (it's a reserved
#                                 internal bucket), creating/renaming TO it
#                                 passed the existing "already exists" check
#                                 and then did self.sections["UNSORTED"]=[]
#                                 (Add) or sections["NEW"]=sections.pop(old)
#                                 with NEW="UNSORTED" (Rename) — both SILENTLY
#                                 WIPED whatever was actually sitting in the
#                                 real unsorted bucket. Reproduced the data
#                                 loss, then added an explicit reserved-name
#                                 check to both paths with a clear status
#                                 message instead. Verified via the real
#                                 dispatch methods (not just the closures in
#                                 isolation) that the unsorted bucket and
#                                 existing category data are untouched and
#                                 the operation is cleanly rejected.
#   v1.7.6 (2026-06-30) — Bug found in full-pipeline double-check.
#                                 find_duplicate_groups() used
#                                 e.get("base", e["slug"]) to fall back to
#                                 the entry's own slug when "base" was
#                                 missing — but parse_entry() ALWAYS sets
#                                 "base" (possibly to "" on a malformed/
#                                 blank column 2), and dict.get()'s default
#                                 only triggers when the key is absent, not
#                                 when it's present-but-falsy. Result: every
#                                 entry with a blank base column in the file
#                                 would get silently grouped together as
#                                 "duplicates" of each other, regardless of
#                                 how unrelated they actually were. Fixed to
#                                 `e.get("base") or e["slug"]`. Verified the
#                                 false-positive is gone and real same-base
#                                 revision groups still detect correctly.
#                                 Also ran a full combined regression across
#                                 every Fix 6/7/8 piece together in one
#                                 scenario: organize+save (master populates)
#                                 -> PICO-8 strip+add-new-revision -> reconcile
#                                 (existing slug recovers, brand-new revision
#                                 correctly stays unsorted rather than being
#                                 guessed) -> duplicate detection correctly
#                                 finds the cross-bucket (categorized vs
#                                 unsorted) revision pair -> save -> prune
#                                 (stale entry dropped, fresh kept) -> export
#                                 -> import-merge onto a second simulated
#                                 device. All steps passed together, not
#                                 just in isolation.
#   v1.7.5 (2026-06-30) — Bug audit + dedicated duplicate-review screen.
#                                 BUG FOUND & FIXED (regression from v1.7.4):
#                                 the action menu (X) caps its panel height
#                                 but had no scroll offset. Adding "Find
#                                 duplicates"/"Export/Import master list"
#                                 pushed the item count past what fits on a
#                                 720x720 panel (14-16 items vs ~12 visible
#                                 rows), silently clipping "Quit" and
#                                 "Cancel" off-screen — act_idx could still
#                                 cycle onto them via DOWN, but they were
#                                 invisible and effectively unreachable in
#                                 practice. Fixed with act_scroll, kept in
#                                 sync by _h_action via _action_visible_rows()
#                                 (shared capacity calc used by both the
#                                 handler and _draw_action so they can't
#                                 drift apart), plus ▲/▼ scroll indicators.
#                                 Verified by simulating 16-item DOWN-cycling
#                                 — every item stays reachable, scroll never
#                                 leaves valid bounds.
#                                 NEW: S_DUPES — replaces the old one-at-a-
#                                 time queued confirm-dialog duplicate flow
#                                 with a real scrollable overview screen
#                                 (UP/DOWN browse groups, A = resolve via
#                                 confirm dialog [keep-latest/keep-both],
#                                 Y = jump into ALL ENTRIES pre-filtered on
#                                 that title for manual side-by-side review,
#                                 B = close). Built _dupes_visible_rows()
#                                 using the exact same geometry constants as
#                                 _draw_dupes() from the start, specifically
#                                 to avoid repeating the action-menu bug.
#                                 Verified: keep-latest removes the correct
#                                 (older) entries by identity and keeps the
#                                 newest revision; keep-both leaves both
#                                 entries untouched; author/title fuzzy
#                                 groups never auto-delete, only point at Y;
#                                 25-group synthetic stress test confirmed
#                                 every group stays reachable across repeated
#                                 DOWN wraparound with no drift.
# Earlier history (v1.0.0–v1.7.4), condensed:
#   v1.7.4 — Fix 8: portable master list (export/import-merge), author/title
#            fuzzy duplicate detection, S_CONFIRM callback-ordering fix.
#   v1.7.3 — Fix 7: persistent master-category JSON (favourites.txt.master.json),
#            append-only slug history; reconcile prefers it over .bak_* scanning.
#   v1.7.2 — Fix 6: PICO-8 category-strip recovery via newest-good .bak_* scan,
#            30%-overlap guard against false positives.
#   v1.7.1 — Feature WW: rename/delete category, duplicate-on-assign warning.
#   v1.7.0 — Feature VV: Suggest New Categories (S_SUGGEST/S_SGFETCH screens).
#   v1.6.4 — Sync UU: ported Pi-version fixes (entry 'base' field, AUTO_SORT_RULES
#            dict format, author-keyword matching, scaled BBS watchdog).
#   v1.6.3 — Fix TT: crash logging added (draw()/handle() wrapped, recover to S_MAIN).
#   v1.6.2 — Fix SS: check_network() false-offline on Anbernic WiFi drivers fixed.
#   v1.6.1 — Fix RR: BBS fetch pre-flight check blocked SDL thread, killed by
#            muOS watchdog — removed; fetch_bbs_tags() handles dead connections itself.
#   v1.6.0 — Feature QQ: marquee scroll for overflowing titles/category names.
#   v1.5.6 — UI PP: left panel header stacked (mode label, count, sort indicator).
#   v1.5.5 — Fix OO: autosort crash — hex int passed to R.fill() instead of RGBA tuple.
#   v1.5.4 — Fix NN: bold-font height caused 4 separate overlap bugs; row Y's adjusted.
#   v1.5.3 — Polish MM: bold font (fbd/fbg) added for titles/headers.
#   v1.5.2 — Polish LL: contrast pass — BG darker, DIM/TEAL/RED/etc. brightened.
#   v1.5.1 — Fix KK: _as_scroll() vis count didn't match _draw_autosort's scaled formula.
#   v1.5.0 — Port JJ: multi-device support — sdl_map + screen size read from muOS config.
#   v1.4.2 — Fix II: no-WiFi toast notification before BBS fetch attempt.
#   v1.4.1 — Fix HH: S_BBSFETCH→S_AUTOSORT transition bug; stale sel_entry; L1/R1 in autosort.
#   v1.4.0 — Port GG: auto-sort + BBS tag fetch ported from Pi version (threaded, queue-drained).
#   v1.3.2 — Rename FF: "Remove entry" → "Delete game" throughout.
#   v1.3.1 — Add EE: category reorder via L2/R2 in cats column.
#   v1.3.0 — Remove DD: A/B swap feature removed entirely (non-functional, confusing).
#            NOTE: buttons_held set in main()'s event loop is a leftover from this
#            feature — it's still tracked but nothing reads it. Not a bug, just dead
#            code; safe to remove if touching that area again.
#   v1.2.1 — Fix CC: r_scroll/r_idx not reset in _sort_cat().
#   v1.2.0 — Fix BB: NameError on L1/R1 in right panel (variable scoped wrong).
#   v1.1.9 — Fix Y/Z: rewrote to raw joystick API; JOY_* constants corrected per device sdl_map.
#   v1.1.7 — Fix R/S: browse scroll desync; unsorted entries written without section header.
#   v1.1.6 — Fix N: _resolve_btn missing on App (crash every press).
#   v1.1.4 — Fix G/H/I: combo ordering, hat clear, L1/R1 no repeat.
#   v1.1.3 — Fix E/F: BTN_BACK index correction; L2/R2 digital button approach.
#   v1.1.2 — Fix A/B/C/D: scroll, held-repeat, clamp, wrap fixes.
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

import ctypes, ctypes.util, json, os, re, shutil, sys, threading, queue, time
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
    "metroidvania":     "METROIDVANIA",
    "run-and-gun":      "PLATFORMERS / ADVENTURE",
    "runner":           "PLATFORMERS / ADVENTURE",
    "narrative":        "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "story":            "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "visual-novel":     "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "walking-sim":      "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "atmospheric":      "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "horror":           "HORROR / STEALTH",
    "stealth":          "HORROR / STEALTH",
    "art":              "ATMOSPHERIC / WALKING SIMS / NARRATIVE",
    "music":            "MUSIC / DEMOSCENE",
    "rhythm":           "RHYTHM",
    "dance":            "RHYTHM",
    "demoscene":        "MUSIC / DEMOSCENE",
    "demo":             "MUSIC / DEMOSCENE",
    "chiptune":         "MUSIC / DEMOSCENE",
    "audio":            "MUSIC / DEMOSCENE",
    "card":             "CARD / BOARD / STRATEGY",
    "board":            "CARD / BOARD / STRATEGY",
    "chess":            "CARD / BOARD / STRATEGY",
    "tabletop":         "CARD / BOARD / STRATEGY",
    "idle":             "IDLE / CLICKER",
    "clicker":          "IDLE / CLICKER",
    "incremental":      "IDLE / CLICKER",
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
    ("SPORTS / PINBALL", {
        "titles":  ["pinball","tennis","golf","soccer","football","basketball",
                    "baseball","bowling","hockey","ball","sport"],
        "authors": [],
    }),
    ("SIM / TYCOON / SANDBOX", {
        "titles":  ["tycoon","theme","craft","city","manage",
                    "delivery","trade","mining","factory","colony"],
        "authors": [],
    }),
    ("HORROR / STEALTH", {
        "titles":  ["horror","scary","fear","creepy","stealth","sneak",
                    "nightmare","haunt","ghost","zombie","slasher","dread"],
        "authors": [],
    }),
    ("RHYTHM", {
        "titles":  ["rhythm","dance","groove","metronome","tapbeat","disco"],
        "authors": [],
    }),
    ("METROIDVANIA", {
        "titles":  ["metroidvania","vania"],
        "authors": [],
    }),
    ("CARD / BOARD / STRATEGY", {
        "titles":  ["card","poker","solitaire","chess","checkers","board",
                    "dice","tabletop","deck"],
        "authors": [],
    }),
    ("IDLE / CLICKER", {
        "titles":  ["idle","clicker","incremental","afk","autoclick"],
        "authors": [],
    }),
    ("CLOCKS / UTILITIES / TOYS", {
        "titles":  ["clock","watch","timer","util","tool","toy",
                    "screensaver","paint","draw","sketch","generator","test"],
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
    # Horror / Stealth
    "horror":            "HORROR / STEALTH",
    "survival-horror":   "HORROR / STEALTH",
    "stealth":           "HORROR / STEALTH",
    # Sports / Pinball
    "sports":            "SPORTS / PINBALL",
    "football":          "SPORTS / PINBALL",
    "soccer":            "SPORTS / PINBALL",
    "basketball":        "SPORTS / PINBALL",
    "baseball":          "SPORTS / PINBALL",
    "golf":              "SPORTS / PINBALL",
    "tennis":            "SPORTS / PINBALL",
    "pinball":           "SPORTS / PINBALL",
    # Card / Board / Strategy
    "card-game":         "CARD / BOARD / STRATEGY",
    "board-game":        "CARD / BOARD / STRATEGY",
    "tabletop":          "CARD / BOARD / STRATEGY",
    "deck-building":     "CARD / BOARD / STRATEGY",
    "poker":             "CARD / BOARD / STRATEGY",
    "chess":             "CARD / BOARD / STRATEGY",
    # Tower Defence — genuinely novel, no existing category covers it
    "tower-defense":     "TOWER DEFENCE",
    "tower-defence":     "TOWER DEFENCE",
    "td":                "TOWER DEFENCE",
    # Sim / Tycoon / Sandbox
    "simulation":        "SIM / TYCOON / SANDBOX",
    "sim":               "SIM / TYCOON / SANDBOX",
    "city-builder":      "SIM / TYCOON / SANDBOX",
    "farming":           "SIM / TYCOON / SANDBOX",
    "management":        "SIM / TYCOON / SANDBOX",
    "tycoon":            "SIM / TYCOON / SANDBOX",
    # Multiplayer — genuinely novel, no existing category covers it
    "multiplayer":       "MULTIPLAYER",
    "co-op":             "MULTIPLAYER",
    "2-player":          "MULTIPLAYER",
    "local-multiplayer": "MULTIPLAYER",
    # Idle / Clicker
    "idle":              "IDLE / CLICKER",
    "clicker":           "IDLE / CLICKER",
    "incremental":       "IDLE / CLICKER",
    # Rhythm
    "rhythm":            "RHYTHM",
    "dance":             "RHYTHM",
    # Metroidvania
    "metroidvania":      "METROIDVANIA",
}

KEYWORD_TO_NEW_CAT = {
    "horror":     "HORROR / STEALTH",
    "zombie":     "HORROR / STEALTH",
    "haunt":      "HORROR / STEALTH",
    "creep":      "HORROR / STEALTH",
    "scary":      "HORROR / STEALTH",
    "terror":     "HORROR / STEALTH",
    "stealth":    "HORROR / STEALTH",
    "sneak":      "HORROR / STEALTH",
    "sport":      "SPORTS / PINBALL",
    "soccer":     "SPORTS / PINBALL",
    "footbal":    "SPORTS / PINBALL",
    "basket":     "SPORTS / PINBALL",
    "tennis":     "SPORTS / PINBALL",
    "golf":       "SPORTS / PINBALL",
    "pinball":    "SPORTS / PINBALL",
    "chess":      "CARD / BOARD / STRATEGY",
    "poker":      "CARD / BOARD / STRATEGY",
    "card":       "CARD / BOARD / STRATEGY",
    "tower def":  "TOWER DEFENCE",
    "idle":       "IDLE / CLICKER",
    "clicker":    "IDLE / CLICKER",
    "farm":       "SIM / TYCOON / SANDBOX",
    "simul":      "SIM / TYCOON / SANDBOX",
    "tycoon":     "SIM / TYCOON / SANDBOX",
    "manage":     "SIM / TYCOON / SANDBOX",
    "rhythm":     "RHYTHM",
    "dance":      "RHYTHM",
    "metroidvania": "METROIDVANIA",
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

def suggest_author_categories(entries, existing_categories):
    """Scan entries for authors with many works not yet covered by an existing
    category. Returns dict: 'AUTHOR COLLECTION' -> [entry, ...] for authors
    with >= MIN_SUGGEST entries, same precedent as the existing MOT COLLECTION
    bucket. An author can be prolific across several genres and still warrant
    a single artist-collection category — entries are not excluded just
    because they also matched a thematic keyword/BBS suggestion.
    """
    from collections import defaultdict
    existing_upper = {c.upper() for c in existing_categories}
    by_author = defaultdict(list)
    for entry in entries:
        author = (entry.get("author") or "").strip()
        if not author:
            continue
        by_author[author.lower()].append(entry)
    out = {}
    for author_lower, ents in by_author.items():
        if len(ents) < MIN_SUGGEST:
            continue
        proposed = f"{author_lower.upper()} COLLECTION"
        if proposed in existing_upper:
            continue
        out[proposed] = ents
    return out


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
    remaining = sections.get("UNSORTED",[]) + unsorted
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
    update_master_categories(path, categories, sections)
    return ts_bak

# =============================================================================
# FIX(bug7): persistent master-category JSON.
#
# .bak_* backups are a good *short-term* safety net (Fix 6) but they rotate
# (only the last 3 are kept) and are themselves taken pre-write, so a run of
# PICO-8 strip events without an intervening app save can age them out.
#
# favourites.master.json sits next to favourites.txt and is a simple,
# append-only slug -> last-known-category record that is NEVER pruned by
# rotation and NEVER touched by PICO-8 (PICO-8 doesn't know it exists). Every
# time the user saves in this app, every categorised slug gets upserted with
# its category + a last_seen timestamp. This becomes the primary source for
# Fix 6 recovery; the .bak_* scan remains as a fallback for slugs the master
# file doesn't know about yet (e.g. its very first run on an existing file).
# =============================================================================

MASTER_SCHEMA_VERSION = 1

def master_path_for(path):
    return path + ".master.json"

def load_master_categories(path):
    """Returns {} on missing/corrupt file — never raises."""
    mpath = master_path_for(path)
    if not os.path.exists(mpath):
        return {}
    try:
        with open(mpath, encoding="utf-8") as f:
            data = json.load(f)
        slugs = data.get("slugs", {})
        return slugs if isinstance(slugs, dict) else {}
    except Exception:
        return {}

def save_master_categories(path, slugs):
    mpath = master_path_for(path)
    tmp = mpath + ".tmp"
    data = {"version": MASTER_SCHEMA_VERSION, "slugs": slugs}
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, mpath)
    except Exception:
        pass  # master file is a convenience layer — never block a save on it

def update_master_categories(path, categories, sections):
    """Upsert slug -> {cat, title, base, last_seen} for every categorised
    entry into the master file. Called automatically from write_file()."""
    slugs = load_master_categories(path)
    now = datetime.now().isoformat(timespec="seconds")
    for cat in categories:
        if cat == "UNSORTED":
            continue
        for e in sections.get(cat, []):
            slugs[e["slug"]] = {
                "cat": cat, "title": e.get("title", ""),
                "base": e.get("base", ""), "last_seen": now,
            }
    save_master_categories(path, slugs)

def set_master_category_for_entries(path, entries, new_cat):
    """
    Directly upsert master records for specific entries to new_cat, WITHOUT
    waiting for the next full write_file() save.

    Why this exists: rename/delete-category only update in-memory state
    (sections/categories) and favourites.txt — the master record otherwise
    wouldn't reflect the change until the user's next "Save file". If PICO-8
    strips favourites.txt in that window, reconcile_stripped_categories()
    would faithfully recover entries into the OLD/deleted category name from
    the stale master record, silently undoing the rename or deletion the
    user just made. Calling this immediately after rename/delete closes
    that window.

    new_cat="UNSORTED" intentionally still writes a record (rather than
    deleting it) so the slug's history (title/base) is preserved for the
    "back up every favourite ever categorized" master-list goal — but
    reconcile_stripped_categories() already excludes cat=="UNSORTED" records
    from its slug->category map, so it will correctly leave these entries
    unsorted instead of resurrecting whatever category they used to be in.
    """
    if not entries:
        return
    slugs = load_master_categories(path)
    now = datetime.now().isoformat(timespec="seconds")
    for e in entries:
        slugs[e["slug"]] = {
            "cat": new_cat, "title": e.get("title", ""),
            "base": e.get("base", ""), "last_seen": now,
        }
    save_master_categories(path, slugs)

def prune_master_categories(path, keep_days=180):
    """Cleanup tool: drop master entries not seen in keep_days. Returns the
    number of entries removed. Safe to call any time (e.g. from a menu
    action) — does nothing destructive to favourites.txt itself."""
    slugs = load_master_categories(path)
    if not slugs:
        return 0
    cutoff = datetime.now().timestamp() - keep_days * 86400
    kept = {}
    removed = 0
    for slug, rec in slugs.items():
        try:
            ts = datetime.fromisoformat(rec.get("last_seen", "")).timestamp()
        except Exception:
            ts = 0  # unparsable/missing timestamp — treat as stale
        if ts >= cutoff:
            kept[slug] = rec
        else:
            removed += 1
    if removed:
        save_master_categories(path, kept)
    return removed

def find_duplicate_groups(sections, unsorted):
    """
    Group entries that share the same 'base' (BBS cart ID) — these are
    likely the same cart at different PICO-8 revisions (slug suffix -N),
    NOT necessarily true duplicates, so this is a review aid, not an
    auto-delete. Returns {base: [entries...]} for every base with >1 entry,
    each group sorted with the highest revision suffix first (best guess
    at "the one to keep").
    """
    by_base = {}
    all_entries = list(unsorted)
    for lst in sections.values():
        all_entries += lst
    for e in all_entries:
        # NOTE: e.get("base", e["slug"]) is WRONG here — dict.get()'s default
        # only applies when the key is missing, not when it's present-but-
        # empty. parse_entry() always sets "base" (possibly to "" on a
        # malformed/blank column), so that pattern would silently group
        # every blank-base entry in the file together as "duplicates" of
        # each other. Use `or` to treat empty string the same as missing.
        key = e.get("base") or e["slug"]
        by_base.setdefault(key, []).append(e)

    def rev_num(e):
        m = re.search(r"-(\d+)$", e["slug"])
        return int(m.group(1)) if m else -1

    groups = {}
    for base, ents in by_base.items():
        if len(ents) > 1:
            groups[base] = sorted(ents, key=rev_num, reverse=True)
    return groups

def _norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", t.lower())

def find_author_title_duplicates(sections, unsorted, exclude_bases=None):
    """
    Catch likely duplicates that DON'T share a base/cart ID — e.g. the same
    cart re-uploaded to the BBS under a new ID by the same author. Groups
    entries with an identical author AND a near-identical normalised title.
    `exclude_bases` lets the caller skip entries already covered by
    find_duplicate_groups() (the more reliable base-ID match) so the same
    pair isn't reported twice.
    """
    exclude_bases = exclude_bases or set()
    all_entries = list(unsorted)
    for lst in sections.values():
        all_entries += lst
    by_key = {}
    for e in all_entries:
        if e.get("base") in exclude_bases:
            continue
        key = (e.get("author", "").strip().lower(), _norm_title(e.get("title", "")))
        if not key[0] or not key[1]:
            continue
        by_key.setdefault(key, []).append(e)
    return {k: v for k, v in by_key.items() if len(v) > 1}

def find_all_duplicate_groups(sections, unsorted):
    """Combined view used by the UI: list of (reason, entries) tuples."""
    groups = []
    base_groups = find_duplicate_groups(sections, unsorted)
    for base, ents in base_groups.items():
        groups.append(("same cart, different revision", ents))
    author_groups = find_author_title_duplicates(sections, unsorted, exclude_bases=set(base_groups))
    for key, ents in author_groups.items():
        groups.append(("same author + title, different cart ID", ents))
    return groups

# =============================================================================
# FIX(bug8): master list as a portable, full-history database.
#
# Because the master JSON already accumulates EVERY slug ever categorised
# (not just what's currently in favourites.txt), it doubles as a portable
# backup of the user's whole organisation history — exportable to another
# file/device and mergeable back in without losing anything on either side.
# =============================================================================

def export_master_categories(path, dest_path):
    """Copy the current master JSON to dest_path (e.g. an SD card root or
    a USB-shared folder) so it can be carried to another device."""
    mpath = master_path_for(path)
    if not os.path.exists(mpath):
        return False, "No master list to export yet — save at least once first."
    try:
        shutil.copy2(mpath, dest_path)
        return True, dest_path
    except Exception as e:
        return False, str(e)

def import_master_categories(path, src_path):
    """
    Merge an external master JSON (e.g. from another device) into this
    file's master list. Per-slug, the record with the newer last_seen wins.
    Never deletes local history that the import doesn't mention. Returns
    (added_count, updated_count) or raises on a genuinely unreadable file.
    """
    with open(src_path, encoding="utf-8") as f:
        incoming = json.load(f).get("slugs", {})
    if not isinstance(incoming, dict):
        return 0, 0
    local = load_master_categories(path)
    added = updated = 0
    for slug, rec in incoming.items():
        if not isinstance(rec, dict) or not rec.get("cat"):
            continue
        cur = local.get(slug)
        if cur is None:
            local[slug] = rec; added += 1
        else:
            try:
                newer = datetime.fromisoformat(rec.get("last_seen","")) > \
                        datetime.fromisoformat(cur.get("last_seen",""))
            except Exception:
                newer = False
            if newer:
                local[slug] = rec; updated += 1
    save_master_categories(path, local)
    return added, updated


#
# When PICO-8/Splore itself saves a NEW favourite to favourites.txt, it
# rewrites the whole file and does NOT understand our "# === CATEGORY ==="
# divider headers — so it drops every header but keeps all entries in their
# original relative (sequential) order. The next time we load the file it
# looks 100% "unsorted" even though the user had it fully organised.
#
# Our own write_file() always leaves a timestamped .bak_* copy behind that
# DOES still have the headers. So on load, if we detect a file with zero
# category headers but a prior backup that had categories, we rebuild a
# slug -> category map from the newest such backup and re-assign each
# current entry to its previous category by slug match (not by position —
# position isn't trustworthy since PICO-8 may have inserted new favourites
# anywhere in the sequence). Anything not found in the map (i.e. genuinely
# new favourites PICO-8 just added) is left unsorted, exactly as before.
#
# This only changes in-memory state on load; nothing is written to disk
# until the user explicitly saves (START), same as every other load path.
# =============================================================================

def find_backups_newest_first(path):
    """Return all .bak_* files for path, newest first."""
    bak_dir  = os.path.dirname(os.path.abspath(path))
    bak_base = os.path.basename(path) + ".bak_"
    try:
        candidates = sorted(
            (f for f in os.listdir(bak_dir) if f.startswith(bak_base)),
            reverse=True,
        )
    except OSError:
        return []
    return [os.path.join(bak_dir, f) for f in candidates]

def reconcile_stripped_categories(path, sections, cat_order, unsorted):
    """
    If the just-loaded file has no category headers at all but a recent
    backup does, rebuild categories from the backup via slug matching.

    Returns (sections, cat_order, unsorted, recovered_count, backup_name)
    where recovered_count is 0 and backup_name is None if no recovery was
    performed (nothing to do, or not enough overlap to trust it).
    """
    if cat_order:
        # File still has headers — nothing stripped, nothing to do.
        return sections, cat_order, unsorted, 0, None

    # Primary source: the persistent master JSON (Fix 7) — never rotates,
    # never stripped by PICO-8, accumulates across the whole project history.
    master = load_master_categories(path)
    slug_to_cat = {slug: rec["cat"] for slug, rec in master.items()
                   if rec.get("cat") and rec["cat"] != "UNSORTED"}
    master_cats_seen = list(dict.fromkeys(rec["cat"] for rec in master.values()
                                           if rec.get("cat") and rec["cat"] != "UNSORTED"))
    source_name = "master record" if slug_to_cat else None

    # Fallback / supplement: scan .bak_* backups newest-to-oldest for any
    # category headers the master file doesn't already cover (e.g. the very
    # first run before a master file existed yet). Backups are copied BEFORE
    # each write, so the newest backup can itself be a stripped snapshot —
    # use the first one that actually still has categories.
    for candidate in find_backups_newest_first(path):
        if not os.path.exists(candidate):
            continue
        try:
            cand_sections, cand_order, _cand_unsorted = parse_file(candidate)
        except Exception:
            continue
        if cand_order:
            for cat in cand_order:
                if cat == "UNSORTED":
                    continue
                for e in cand_sections.get(cat, []):
                    slug_to_cat.setdefault(e["slug"], cat)
                    if cat not in master_cats_seen:
                        master_cats_seen.append(cat)
            if source_name is None:
                source_name = os.path.basename(candidate)
            break

    if not slug_to_cat:
        return sections, cat_order, unsorted, 0, None

    # Sanity check: only proceed if a meaningful fraction of the CURRENT
    # entries are recognised. A low-overlap result is more likely an
    # unrelated/very-old record than a genuine PICO-8 strip event, so we
    # play it safe and leave everything unsorted in that case.
    total_current = len(unsorted) + sum(len(v) for v in sections.values())
    if total_current == 0:
        return sections, cat_order, unsorted, 0, None

    matched = sum(1 for e in unsorted if e["slug"] in slug_to_cat)
    if matched / total_current < 0.3:
        return sections, cat_order, unsorted, 0, None

    new_sections = {cat: [] for cat in master_cats_seen}
    new_unsorted = []
    for e in unsorted:
        cat = slug_to_cat.get(e["slug"])
        if cat and cat != "UNSORTED":
            new_sections.setdefault(cat, []).append(e)
        else:
            new_unsorted.append(e)

    if "UNSORTED" not in new_sections:
        new_sections["UNSORTED"] = []

    return new_sections, master_cats_seen + ["UNSORTED"], new_unsorted, matched, source_name

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
S_DUPES    = "DUPES"    # scrollable duplicate-group review screen

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
        self.confirm_skip_cb = None
        self.dupes_groups = []
        self.dupes_idx = 0
        self.dupes_scroll = 0
        self.act_scroll = 0

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
            sec, order, uns, recovered, bak_name = reconcile_stripped_categories(path, sec, order, uns)
        except Exception as e:
            self.status="Parse error: "+str(e); self.status_ok=False; return
        self.filepath=path; self.sections=sec
        self.cat_order=order; self.unsorted=uns
        # BUG FIX (revert correctness): merge against DEFAULT_CATS, NOT
        # self.categories. Merging against self.categories would let an
        # unsaved in-memory category (e.g. "Add category" never followed by
        # "Save file") survive a reload/revert, since it's still sitting in
        # self.categories at the moment this runs. Any category that was
        # actually saved is safe regardless — write_file() always persists
        # a header for every category (even empty ones), so it comes back
        # via `order` from the file itself.
        merged=list(order)
        for c in DEFAULT_CATS:
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
        if recovered:
            self.status=(f"{os.path.basename(path)}  |  PICO-8 stripped categories — "
                          f"recovered {recovered} from {bak_name}  |  press START to save")
        else:
            self.status=f"{os.path.basename(path)}  |  {uns_n} unsorted  |  {total} total"
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

    def _reload_file(self):
        """'Revert all changes' — re-parse favourites.txt from disk, throwing
        away every in-memory edit made since the last Save (moves, renames,
        new/deleted categories, sort order, dedup resolutions, etc). What's
        on disk is untouched by this — it's the same _load() path used at
        startup, so it also re-runs Fix 6/7 strip recovery if needed."""
        if not self.filepath:
            self.status = "No file loaded."; self.status_ok = False; return
        self.confirm_msg = ("Discard all changes since the last Save and "
                             "reload from disk? This cannot be undone.")
        def _do_reload():
            self._load(self.filepath)
            self.status = "Reloaded from disk — unsaved changes discarded."
            self.status_ok = True
        self.confirm_cb = _do_reload
        self.confirm_skip_cb = None
        self.screen = S_CONFIRM

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
        elif self.screen==S_DUPES:      self._h_dupes(btn)
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
            removed_from = self.unsorted
            if not _remove_by_id(self.unsorted):
                removed_from = self.sections.get("UNSORTED",[])
                _remove_by_id(removed_from)
        else:
            removed_from = self.sections.get(src,[])
            _remove_by_id(removed_from)
        # Duplicate check — warn if same slug already in target
        if target_cat not in self.sections: self.sections[target_cat]=[]
        existing_slugs = {x["slug"] for x in self.sections[target_cat]}
        if e["slug"] in existing_slugs:
            # Ask user rather than silently deduplicating (Pi version deduped silently).
            # BUG FIX: e was already removed from its source list above (so the
            # duplicate check above sees the post-removal state). If the user
            # declines this dialog, e must go back to `removed_from`, or it's
            # orphaned — gone from every list with no way to recover it short
            # of reloading the file. confirm_skip_cb (B) restores it.
            self.confirm_msg = (f"'{ e['title'][:34]}' may already be in '{target_cat}'. Move anyway?")
            def _do_move(entry=e, tcat=target_cat):
                self.sections[tcat].append(entry)
                self.sel_entry=None
                self._rebuild_all_flat()
                self.status=f"Moved '{entry['title'][:36]}' → {tcat} (duplicate warning)"
                self.status_ok=True
                self.R.flush()
            def _do_cancel_move(entry=e, restore_to=removed_from):
                restore_to.append(entry)
                self.sel_entry=None
                self._rebuild_all_flat()
                self.status=f"Move cancelled — '{entry['title'][:36]}' stayed put."
                self.status_ok=True
                self.R.flush()
            self.confirm_cb=_do_move
            self.confirm_skip_cb=_do_cancel_move
            self.screen=S_CONFIRM
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
            if new_name == "UNSORTED":
                # Same reserved-name hazard as Add category: this would
                # overwrite self.sections["UNSORTED"], wiping real unsorted
                # entries rather than creating a real category.
                self.status = "'UNSORTED' is reserved — pick a different name."
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
            # Keep the master record in sync NOW, not just at next save —
            # otherwise a PICO-8 strip before the next save would recover
            # entries back under the OLD category name (see Fix 9).
            if self.filepath:
                set_master_category_for_entries(self.filepath, self.sections[new_name], new_name)
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
            # Keep the master record in sync NOW (Fix 9) — otherwise these
            # slugs' stale master entries still say cat=c, and a PICO-8
            # strip before the next save would resurrect the just-deleted
            # category. Mark them UNSORTED instead of erasing their master
            # history entirely, since reconcile already excludes UNSORTED
            # records from its recovery map.
            if self.filepath:
                set_master_category_for_entries(self.filepath, ents, "UNSORTED")
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
        items=["Save file","Reload file (discard changes)","Add category",
               "Delete game","Filter all entries",
               "Clear filter","Auto-sort unsorted","Fetch BBS tags",
               "Suggest new categories","Find duplicates",
               "Export master list","Import master list"]
        # Context: category-specific items when a category is open
        if self.sel_cat:
            items += ["Rename category","Delete category"]
        items += ["Change file path","Quit","Cancel"]
        self.act_items=items; self.act_idx=0; self.act_scroll=0; self.screen=S_ACTION

    def _action_visible_rows(self):
        item_h = _sy(48)
        mh = min(len(self.act_items)*item_h + _sy(60), SH-_sy(80))
        return max(1, (mh - _sy(38)) // item_h)

    def _h_action(self, btn):
        if btn=="UP":   self.act_idx=(self.act_idx-1)%len(self.act_items)
        elif btn=="DOWN": self.act_idx=(self.act_idx+1)%len(self.act_items)
        elif btn in ("A","RIGHT"): self._do_action(self.act_items[self.act_idx]); return
        elif btn in ("B","X"):     self.screen=S_MAIN; return
        visible = self._action_visible_rows()
        if self.act_idx < self.act_scroll:
            self.act_scroll = self.act_idx
        elif self.act_idx >= self.act_scroll + visible:
            self.act_scroll = self.act_idx - visible + 1

    def _do_action(self, action):
        self.screen=S_MAIN
        if action=="Save file":
            self._save()
        elif action=="Reload file (discard changes)":
            self._reload_file()
        elif action=="Add category":
            self.kb=VKeyboard("New category name (will be uppercased):","")
            def _add(name):
                name=name.strip().upper()
                if not name:
                    return
                if name == "UNSORTED":
                    # "UNSORTED" is a reserved internal bucket name, not a
                    # real category — creating one here would silently wipe
                    # self.sections["UNSORTED"] (the actual unsorted entries
                    # bucket), losing real data.
                    self.status = "'UNSORTED' is reserved — pick a different name."
                    self.status_ok = False
                    return
                if name not in self.categories:
                    self.categories.append(name); self.sections[name]=[]
                    self.status=f"Category added: {name}"; self.status_ok=True
                else:
                    self.status = f"'{name}' already exists."; self.status_ok = False
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
        elif action=="Find duplicates":
            self._start_duplicate_review()
        elif action=="Export master list":
            default_dest = os.path.join(os.path.dirname(self.filepath), "favourites_master_export.json") \
                           if self.filepath else "favourites_master_export.json"
            self.kb = VKeyboard("Export master list to path:", default_dest)
            def _do_export(dest):
                ok, info = export_master_categories(self.filepath, dest)
                if ok:
                    self.status = f"Master list exported to {info}"; self.status_ok=True
                else:
                    self.status = f"Export failed: {info}"; self.status_ok=False
            self._kb_cb = _do_export; self.screen = S_KEYBOARD
        elif action=="Import master list":
            self.kb = VKeyboard("Import master list from path:", "")
            def _do_import(src):
                try:
                    added, updated = import_master_categories(self.filepath, src)
                    self.status = f"Master list merged: {added} new, {updated} updated"
                    self.status_ok = True
                except Exception as e:
                    self.status = f"Import failed: {e}"; self.status_ok = False
            self._kb_cb = _do_import; self.screen = S_KEYBOARD
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

    # ── duplicate review (scrollable overview screen) ───────────────────────────

    def _start_duplicate_review(self):
        groups = find_all_duplicate_groups(self.sections, self.unsorted)
        if not groups:
            self.status = "No likely duplicates found."; self.status_ok = True
            return
        self.dupes_groups = groups
        self.dupes_idx = 0
        self.dupes_scroll = 0
        self.screen = S_DUPES

    def _dupes_visible_rows(self):
        # Must match the panel geometry used in _draw_dupes() exactly, or
        # the handler's scroll math and the renderer's visible window can
        # drift apart (the same class of bug just fixed in the action menu).
        bh = SH - _sy(106)
        card_h = _sy(56)
        return max(2, (bh - _sy(34)) // card_h)

    def _h_dupes(self, btn):
        if not self.dupes_groups:
            self.screen = S_MAIN; return
        n = len(self.dupes_groups)
        if btn=="UP":
            self.dupes_idx=(self.dupes_idx-1)%n
        elif btn=="DOWN":
            self.dupes_idx=(self.dupes_idx+1)%n
        elif btn in ("B","X"):
            self.screen = S_MAIN; return
        elif btn=="Y":
            # Jump into ALL ENTRIES filtered on this group's title, for
            # manual side-by-side review (useful for the author/title
            # fuzzy matches that this screen won't auto-resolve).
            _reason, ents = self.dupes_groups[self.dupes_idx]
            self.browse_mode = True
            self.all_filter  = ents[0]["title"]
            self._rebuild_all_flat()
            self.l_idx = self.l_scroll = 0
            self.focus = F_LEFT
            self.status = f"Filtered ALL ENTRIES by '{ents[0]['title'][:30]}' for manual review."
            self.status_ok = True
            self.screen = S_MAIN
            return
        elif btn=="A":
            self._resolve_dupes_group(self.dupes_idx)
            return
        visible = self._dupes_visible_rows()
        if self.dupes_idx < self.dupes_scroll:
            self.dupes_scroll = self.dupes_idx
        elif self.dupes_idx >= self.dupes_scroll + visible:
            self.dupes_scroll = self.dupes_idx - visible + 1

    def _resolve_dupes_group(self, idx):
        if idx >= len(self.dupes_groups):
            return
        reason, ents = self.dupes_groups[idx]

        if reason == "same author + title, different cart ID":
            # No reliable "which is newer" signal across different cart IDs
            # — don't guess. Point at the manual-review path instead.
            self.status = "No reliable recency signal for this group — press Y to review it in ALL ENTRIES."
            self.status_ok = True
            return

        keep = ents[0]   # base-ID groups are sorted newest-revision-first
        drop = ents[1:]
        names = ", ".join(f"'{e['title'][:24]}'" for e in drop)
        self.confirm_msg = (
            f"Keep '{keep['title'][:28]}', remove {len(drop)} older "
            f"[{names}]? (B = keep both)")

        def _do_keep_latest(idx=idx, keep=keep, drop=list(drop)):
            self._remove_entries_by_identity(drop)
            self._rebuild_all_flat()
            if idx < len(self.dupes_groups):
                del self.dupes_groups[idx]
            self.dupes_idx = max(0, min(self.dupes_idx, len(self.dupes_groups)-1))
            self.status = f"Kept '{keep['title'][:28]}', removed {len(drop)} duplicate(s)."
            self.status_ok = True
            self.screen = S_DUPES if self.dupes_groups else S_MAIN

        def _do_keep_both(idx=idx):
            if idx < len(self.dupes_groups):
                del self.dupes_groups[idx]
            self.dupes_idx = max(0, min(self.dupes_idx, len(self.dupes_groups)-1))
            self.screen = S_DUPES if self.dupes_groups else S_MAIN

        self.confirm_cb = _do_keep_latest
        self.confirm_skip_cb = _do_keep_both
        self.screen = S_CONFIRM

    def _remove_entries_by_identity(self, entries_to_remove):
        """Removes entries from unsorted + every category by object identity
        (never by ==/slug), per the project's core duplicate-bug rule."""
        targets = list(entries_to_remove)
        for lst in [self.unsorted] + list(self.sections.values()):
            for t in targets:
                for i, e in enumerate(lst):
                    if e is t:
                        del lst[i]
                        break

    def _h_confirm(self, btn):
        if btn=="A":
            cb=self.confirm_cb
            self.confirm_cb=None; self.confirm_skip_cb=None; self.screen=S_MAIN
            if cb: cb()
        elif btn in ("B","X"):
            skip=self.confirm_skip_cb
            self.confirm_cb=None; self.confirm_skip_cb=None; self.screen=S_MAIN
            if skip: skip()

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
        """Compute merged keyword + BBS + author suggestions, return sorted card list.
        Card: {name:str, entries:[entry,...], selected:bool}
        BBS wins over keyword when entry count is higher (Pi version rule).
        Author-collection cards are independent of theme cards — names never
        collide ('X COLLECTION' vs genre names) so they're simply unioned in.
        """
        pool = self._sg_get_pool()

        kw_sugs     = suggest_new_categories(pool, self.categories)
        bbs_sugs    = (suggest_new_categories_from_tags(self._sg_tag_cache, self.categories)
                       if self._sg_tag_cache else {})
        author_sugs = suggest_author_categories(pool, self.categories)

        merged = dict(kw_sugs)
        for cat, ents in bbs_sugs.items():
            if cat not in merged or len(ents) > len(merged[cat]):
                merged[cat] = ents
        merged.update(author_sugs)

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
                found = False
                for lst_name, lst in list(self.sections.items()) + [("__unsorted__", self.unsorted)]:
                    actual = self.unsorted if lst_name == "__unsorted__" else lst
                    for i, e in enumerate(actual):
                        if e is entry:
                            actual.pop(i)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    # Already moved by an earlier selected card this pass
                    # (e.g. matched both a theme cluster and an author
                    # cluster) — do NOT append again, that would duplicate
                    # the entry across two categories.
                    skipped += 1
                    continue
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

    def _draw_dupes(self):
        R = self.R
        groups = self.dupes_groups
        n = len(groups)

        bx, by = _sx(10), _sy(48)
        bw, bh = SW - _sx(20), SH - _sy(106)
        R.fill(bx, by, bw, bh, PANEL)
        R.box(bx, by, bw, bh, ACCENT)
        R.text(f"Possible Duplicates  ({n} group{'s' if n!=1 else ''})",
               bx+_sx(10), by+_sy(6), YELLOW, R.fbg)
        R.hline(bx, by+_sy(28), bw, DIM)

        if not n:
            R.text("No duplicates remaining.", bx+_sx(10), by+_sy(44), DIM, R.fmd)
        else:
            card_h = _sy(56)
            vis    = self._dupes_visible_rows()
            list_y = by + _sy(32)
            for i in range(vis):
                gi = self.dupes_scroll + i
                if gi >= n:
                    break
                reason, ents = groups[gi]
                ry  = list_y + i * card_h
                sel = (gi == self.dupes_idx)
                if sel:
                    R.fill(bx+_sx(4), ry, bw-_sx(8), card_h-_sy(2), SEL_BG)
                R.box(bx+_sx(4), ry, bw-_sx(8), card_h-_sy(2), ACCENT if sel else DIM)
                reason_col = TEAL if reason=="same author + title, different cart ID" else YELLOW
                R.text(reason, bx+_sx(12), ry+_sy(4), reason_col, R.fsm)
                names = "  /  ".join(e["title"][:22] for e in ents[:4])
                if len(ents) > 4:
                    names += f"  (+{len(ents)-4} more)"
                R.text_clip(names, bx+_sx(12), ry+_sy(26), bw-_sx(32), WHITE, R.fmd)

            if self.dupes_scroll > 0:
                R.text("▲", bx+bw-_sx(28), list_y+_sy(2), ACCENT, R.fsm)
            if self.dupes_scroll+vis < n:
                R.text("▼", bx+bw-_sx(28), by+bh-_sy(30), ACCENT, R.fsm)

        R.text("A=Resolve  Y=Review in ALL ENTRIES  B=Close",
               bx+_sx(10), by+bh-_sy(20), DIM, R.fsm)

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
        elif self.screen==S_DUPES:
            self._draw_main_bg()
            self._draw_dupes()
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
        # FIX(menu-scroll): when the item count exceeds the visible capacity,
        # scroll the list (act_scroll, kept in sync by _h_action) instead of
        # silently clipping items like "Quit"/"Cancel" off-screen and unreachable.
        item_h=_sy(48); item_sel_h=_sy(44)
        mw=_sx(400)
        mh=min(len(self.act_items)*item_h+_sy(60), SH-_sy(80))
        mx=(SW-mw)//2; my=(SH-mh)//2
        R.fill(mx,my,mw,mh,PANEL)
        R.box(mx,my,mw,mh,ACCENT)
        R.text("ACTION MENU",mx+_sx(12),my+_sy(8),ACCENT,R.fbg)
        R.hline(mx,my+_sy(32),mw,DIM)
        visible = self._action_visible_rows()
        window = self.act_items[self.act_scroll:self.act_scroll+visible]
        for row,item in enumerate(window):
            i = self.act_scroll + row
            iy=my+_sy(38)+row*item_h
            if iy+item_sel_h > my+mh: break
            if i==self.act_idx:
                R.fill(mx+_sx(4),iy,mw-_sx(8),item_sel_h,SEL_BG)
                R.box(mx+_sx(4),iy,mw-_sx(8),item_sel_h,ACCENT)
            R.text(item,mx+_sx(16),iy+_sy(12),WHITE if i==self.act_idx else DIM,R.fmd)
        if self.act_scroll > 0:
            R.text("▲",mx+mw-_sx(24),my+_sy(36),ACCENT,R.fsm)
        if self.act_scroll+visible < len(self.act_items):
            R.text("▼",mx+mw-_sx(24),my+mh-_sy(40),ACCENT,R.fsm)
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

_BOOT_LOG = "/tmp/pico8sorter_crash.log"

def _boot_log(msg):
    """Best-effort write to the crash log. Startup has no other way to
    surface a failure — muOS gives the process no console, so an
    uncaught exception here previously meant total silence."""
    try:
        with open(_BOOT_LOG, "a") as _f:
            _f.write(msg)
    except Exception:
        pass

def _boot():
    """Everything that has to succeed before the main loop's own
    try/except (in fire()/draw()) is even running. Wrapped end-to-end
    so a boot failure gets logged instead of dying silently."""
    SDL.SDL_GetError.restype = ctypes.c_char_p

    if SDL.SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK) != 0:
        _boot_log(f"\n--- SDL_Init failed: {SDL.SDL_GetError()} ---\n")
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
    if not win:
        _boot_log(f"\n--- SDL_CreateWindow failed ({SW}x{SH}): {SDL.SDL_GetError()} ---\n")
        sys.exit("SDL_CreateWindow failed")

    rend=SDL.SDL_CreateRenderer(win,-1,2)
    if not rend:
        rend=SDL.SDL_CreateRenderer(win,-1,1)
    if not rend:
        _boot_log(f"\n--- SDL_CreateRenderer failed (accelerated and software): {SDL.SDL_GetError()} ---\n")
        sys.exit("SDL_CreateRenderer failed")

    SDL.SDL_JoystickOpen(0)
    SDL.SDL_JoystickEventState(1)

    try:
        R=Renderer(win,rend,find_font(),find_bold_font())
    except Exception:
        import traceback
        _boot_log("\n--- Renderer() init crash ---\n")
        with open(_BOOT_LOG, "a") as _f:
            traceback.print_exc(file=_f)
        raise

    try:
        app=App(R)
    except Exception:
        import traceback
        _boot_log("\n--- App() init crash (likely favourites.txt load/parse/reconcile) ---\n")
        with open(_BOOT_LOG, "a") as _f:
            traceback.print_exc(file=_f)
        raise

    return win, rend, R, app

def main():
    win, rend, R, app = _boot()

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
