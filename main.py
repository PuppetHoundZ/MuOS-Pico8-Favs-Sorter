#!/usr/bin/env python3
# =============================================================================
# PICO-8 Favourites Sorter — muOS Edition  v1.3.2
# For: Anbernic RG Cube XX (720×720) running MustardOS
# Pure Python 3 + SDL2 via ctypes. No pip, no extras needed.
#
# Changelog:
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

import ctypes, ctypes.util, os, re, shutil, sys
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
JOY_A     = 3    # a:b3     South face (A)
JOY_B     = 4    # b:b4     East face  (B)
JOY_Y     = 5    # y:b5     West face  (Y)
JOY_X     = 6    # x:b6     North face (X)
JOY_L     = 7    # leftshoulder:b7   (L1)
JOY_R     = 8    # rightshoulder:b8  (R1)
JOY_BACK  = 9    # back:b9           (SELECT)
JOY_START = 10   # start:b10         (START)
JOY_L3    = 12   # leftstick:b12     (L3, unused)
JOY_L2    = 13   # lefttrigger:b13   (L2, digital)
JOY_R2    = 14   # righttrigger:b14  (R2, digital)
JOY_R3    = 15   # rightstick:b15    (R3, unused)

# Colours RGBA tuples
BG      = (17,  17,  24,  255)
PANEL   = (25,  25,  34,  255)
ACCENT  = (30, 189, 209,  255)
YELLOW  = (255,236,  39,  255)
WHITE   = (224,224, 240,  255)
DIM     = (80,  80, 100,  255)
SEL_BG  = (42,  31,  90,  255)
GREEN   = (30, 215,  96,  255)
RED     = (180, 40,  40,  255)
PURPLE  = (100, 70, 160,  255)
TEAL    = (74, 143, 168,  255)
ORANGE  = (220,140,  40,  255)

SW, SH  = 720, 720
FPS     = 30
ROW_H          = 44
VISIBLE        = 13   # rows visible per list (normal mode, ROW_H=44)
VISIBLE_BROWSE = 10   # rows visible in browse mode (row_h=54, h=610, LIST_Y offset=36)

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

def find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

# =============================================================================
# Renderer
# =============================================================================

class Renderer:
    def __init__(self, win, rend, font_path):
        self.win  = win
        self.rend = rend
        self._cache = {}
        self.fsm = self.fmd = self.flg = None
        if HAS_TTF and font_path:
            fp = font_path.encode()
            self.fsm = TTF.TTF_OpenFont(fp, 15)
            self.fmd = TTF.TTF_OpenFont(fp, 19)
            self.flg = TTF.TTF_OpenFont(fp, 25)

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
    return {
        "raw":    line,
        "slug":   parts[1].strip(),
        "author": parts[4].strip(),
        "title":  parts[6].strip() if len(parts) > 6 else parts[2].strip(),
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
        bx,by,bw,bh = 30,130,660,440
        r.fill(bx,by,bw,bh,PANEL)
        r.box(bx,by,bw,bh,ACCENT)
        r.text(self.prompt, bx+12, by+10, ACCENT, r.flg)
        # text field
        r.fill(bx+10,by+48,bw-20,34,BG)
        r.box(bx+10,by+48,bw-20,34,DIM)
        display = (self.text or "")+"_"
        r.text_clip(display, bx+16, by+54, bw-32, WHITE, r.fmd)
        # keys
        ky = by+100
        for ri,row in enumerate(KB_ROWS):
            n    = len(row)
            kw   = min(80,(bw-20)//n-4)
            totw = n*(kw+4)-4
            sx   = bx+(bw-totw)//2
            for ci,key in enumerate(row):
                kx   = sx+ci*(kw+4)
                isel = (ri==self.row and ci==self.col)
                bg   = ACCENT if isel else (45,45,60,255)
                fg   = BG     if isel else WHITE
                r.fill(kx,ky,kw,36,bg)
                lbl  = key[:6]
                tw   = r.text_w(lbl.upper(),r.fsm)
                r.text(lbl.upper(), kx+(kw-tw)//2, ky+10, fg, r.fsm)
            ky+=44
        r.text("A=Type  B/CANCEL=Abort  DONE=Confirm",bx+12,by+bh-26,DIM,r.fsm)

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
        elif btn=="RIGHT":
            if self.focus==F_LEFT:  self.focus=F_CATS
            elif self.focus==F_CATS and self.sel_cat: self.focus=F_RIGHT

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
        # add to target
        if target_cat not in self.sections: self.sections[target_cat]=[]
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

    # ── action menu ───────────────────────────────────────────────────────────

    def _open_action(self):
        items=["Save file","Add category","Delete game","Filter all entries",
               "Clear filter","Change file path","Quit","Cancel"]
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
        else:
            self._draw_main_bg()
            if self.screen==S_ACTION:   self._draw_action()
            elif self.screen==S_CONFIRM: self._draw_confirm()
            elif self.screen in (S_KEYBOARD,S_FILTER) and self.kb:
                self.kb.draw(R)
        R.present()

    def _draw_nofile(self):
        R=self.R
        R.text("PICO-8 Favourites Sorter",16,18,YELLOW,R.flg)
        R.text("favourites.txt not found.",16,72,WHITE,R.fmd)
        R.text("Press A to enter the path manually.",16,104,DIM,R.fsm)
        R.text(f"HOME={os.environ.get('HOME','?')}",16,126,TEAL,R.fsm)
        y=156; R.text("Searched:",16,y,DIM,R.fsm); y+=20
        for p in SEARCH_PATHS:
            R.text_clip(p,26,y,SW-32,DIM,R.fsm); y+=18
        R.fill(0,SH-34,SW,34,PANEL)
        R.text(self._hint(),8,SH-24,DIM,R.fsm)

    def _draw_main_bg(self):
        R=self.R
        # ── title bar ────────────────────────────────────────────────────────
        R.fill(0,0,SW,44,PANEL)
        R.text("PICO-8 Favourites Sorter",8,6,YELLOW,R.flg)

        # status bar — sits just below content (content bottom = CY+CH = 660)
        # y=668 gives a clean 8px gap above the hint bar panel at y=686
        sc=ACCENT if self.status_ok else RED
        R.text_clip(self.status,8,668,SW-16,sc,R.fsm)

        # ── hint bar ─────────────────────────────────────────────────────────
        R.fill(0,SH-34,SW,34,PANEL)
        R.hline(0,SH-34,SW,DIM)
        R.text_clip(self._hint(),8,SH-24,SW-16,DIM,R.fsm)

        # ── three columns ────────────────────────────────────────────────────
        # LEFT  x=0    w=222
        # CATS  x=228  w=242
        # RIGHT x=476  w=244
        CY=50; CH=SH-50-60   # leave 60px: 20 status + 34 hint + 6 gap
        LX,LW = 0,   222
        CX,CW = 228, 242
        RX,RW = 476, 244

        self._draw_left(LX,CY,LW,CH)
        self._draw_cats(CX,CY,CW,CH)
        self._draw_right(RX,CY,RW,CH)

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
        R.text_clip(mode_lbl, x+6, y+6, w-60, mode_col if focused else DIM, R.fsm)

        le=self._left_entries()
        n=len(le)
        # count + filter indicator
        extra=""
        if bm and self.all_filter:
            extra=f"  filter:'{self.all_filter[:8]}'"
        cnt_lbl=f"({n}){extra}"
        R.text_clip(cnt_lbl, x+w-6-R.text_w(cnt_lbl,R.fsm), y+6, w//2, DIM, R.fsm)

        # sort indicator (browse mode)
        if bm:
            names=["Name","Author","Cat"]
            d="▲" if self.all_sort_asc else "▼"
            sort_lbl=f"{names[self.all_sort_col]}{d}"
            R.text(sort_lbl, x+6, y+22, TEAL, R.fsm)

        LIST_Y = y+36 if bm else y+24
        row_h  = ROW_H if not bm else 54   # 3-line rows in browse mode
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
            R.text_clip(e["title"],x+7,ry+3,w-14,tc,R.fsm)
            R.text_clip(e["author"],x+7,ry+19,w-14,DIM,R.fsm)
            if bm and cat:
                R.text_clip(cat,x+7,ry+35,w-14,TEAL,R.fsm)

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
        R.text("CATEGORIES",x+6,y+6,ACCENT if focused else DIM,R.fsm)

        vis=max(1,(h-28)//ROW_H)
        n=len(self.categories)
        for i in range(vis):
            ci=self.c_scroll+i
            if ci>=n: break
            cat=self.categories[ci]
            ry=y+28+i*ROW_H
            is_cur=(ci==self.c_idx and focused)
            is_act=(cat==self.sel_cat)
            cnt=len(self.sections.get(cat,[]))

            if is_cur:  R.fill(x+3,ry,w-6,ROW_H-2,SEL_BG)
            if is_act:  R.fill(x+3,ry,w-6,ROW_H-2,PURPLE)
            if is_cur or is_act: R.box(x+3,ry,w-6,ROW_H-2,ACCENT if is_cur else PURPLE)

            lc=WHITE if (is_cur or is_act) else DIM
            R.text_clip(cat,x+7,ry+5,w-46,lc,R.fsm)
            cs=str(cnt)
            R.text(cs,x+w-6-R.text_w(cs,R.fsm),ry+5,DIM,R.fsm)

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
        R.text_clip(cat_lbl,x+6,y+6,w-60,ACCENT if focused else DIM,R.fsm)
        re=self._right_entries()
        cnt_s=f"({len(re)})" if self.sel_cat else ""
        if cnt_s:
            R.text(cnt_s,x+w-6-R.text_w(cnt_s,R.fsm),y+6,DIM,R.fsm)

        vis=max(1,(h-28)//ROW_H)
        n=len(re)
        for i in range(vis):
            ri=self.r_scroll+i
            if ri>=n: break
            e=re[ri]; ry=y+28+i*ROW_H
            is_cur=(ri==self.r_idx and focused)
            is_sel=(self.sel_entry is not None and self.sel_entry.get("entry") is e)

            if is_cur: R.fill(x+3,ry,w-6,ROW_H-2,SEL_BG)
            if is_sel: R.box(x+3,ry,w-6,ROW_H-2,ACCENT)

            tc=YELLOW if is_sel else WHITE
            R.text_clip(e["title"],x+7,ry+5,w-14,tc,R.fsm)
            R.text_clip(e["author"],x+7,ry+21,w-14,DIM,R.fsm)

        if n>vis:
            bh=max(16,h*vis//n)
            by=y+(h-bh)*self.r_scroll//max(1,n-vis)
            R.fill(x+w-5,by,3,bh,DIM)

    def _draw_action(self):
        R=self.R
        # FIX(menu-overflow): cap height so adding items never pushes menu off-screen.
        # FIX(menu-clip): guard the render loop so items beyond the capped box
        # boundary are not drawn outside the panel.
        mw=400
        # +60 (not +48): gives 4px clearance between last item and footer text.
        # +48 caused the footer ("↑↓=Move…") to overlap the last item by 8px.
        mh=min(len(self.act_items)*48+60, SH-80)
        mx=(SW-mw)//2; my=(SH-mh)//2
        R.fill(mx,my,mw,mh,PANEL)
        R.box(mx,my,mw,mh,ACCENT)
        R.text("ACTION MENU",mx+12,my+8,ACCENT,R.fmd)
        R.hline(mx,my+32,mw,DIM)
        for i,item in enumerate(self.act_items):
            iy=my+38+i*48
            if iy+44 > my+mh: break   # item would render outside box boundary
            if i==self.act_idx:
                R.fill(mx+4,iy,mw-8,44,SEL_BG)
                R.box(mx+4,iy,mw-8,44,ACCENT)
            R.text(item,mx+16,iy+12,WHITE if i==self.act_idx else DIM,R.fmd)
        R.text("↑↓=Move  A=Select  B=Close",mx+12,my+mh-22,DIM,R.fsm)

    def _draw_confirm(self):
        R=self.R
        mw,mh=460,150
        mx=(SW-mw)//2; my=(SH-mh)//2
        R.fill(mx,my,mw,mh,PANEL)
        R.box(mx,my,mw,mh,RED)
        R.text("Confirm Action",mx+12,my+10,RED,R.fmd)
        R.hline(mx,my+36,mw,DIM)
        R.text_clip(self.confirm_msg,mx+12,my+52,mw-24,WHITE,R.fmd)
        R.text("A=Yes  B=No",mx+12,my+mh-26,DIM,R.fsm)

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

    win=SDL.SDL_CreateWindow(b"PICO-8 Favourites Sorter",
        SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,SW,SH,0)
    rend=SDL.SDL_CreateRenderer(win,-1,2)
    if not rend:
        rend=SDL.SDL_CreateRenderer(win,-1,1)

    SDL.SDL_JoystickOpen(0)
    SDL.SDL_JoystickEventState(1)

    R=Renderer(win,rend,find_font())
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
        app.handle(btn)
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

        app.draw()
        el=SDL.SDL_GetTicks()-t0
        if el<ms: SDL.SDL_Delay(ms-el)

    SDL.SDL_Quit()

if __name__=="__main__":
    main()
