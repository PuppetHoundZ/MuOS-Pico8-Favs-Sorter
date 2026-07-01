# PICO-8 Favourites Sorter — muOS Edition

A controller-only PICO-8 Splore favourites organizer for the Anbernic RG CubeXX-H
running MustardOS (muOS). Pure Python 3 + SDL2 (via `ctypes`) — no `pip`
dependencies, no keyboard/browser required. Built for a 720×720 display and
raw joystick input.

Current version: **v1.7.12**

A companion Raspberry Pi / desktop Linux build (GTK3) is included as the
reference implementation: `pico8-fav-sorter-manager.sh`.

---

## Features

### Core organizing
- Two/three-panel browse-and-sort UI: Unsorted list, Categories, and
  entries-within-category, navigable entirely with a D-pad + face buttons.
- Move entries between Unsorted and any category, or reorder within a
  category, without touching a keyboard.
- ALL ENTRIES browse mode showing author + category per cart, with marquee
  scrolling for titles/authors too long to fit their column.
- 15 built-in genre categories covering Platformers/Adventure, Puzzle,
  Shooters/Space, Racing/Flying/Action, Atmospheric/Walking Sims,
  Music/Demoscene, Clocks/Utilities/Toys, Sports/Pinball,
  Sim/Tycoon/Sandbox, Horror/Stealth, Rhythm, Metroidvania,
  Card/Board/Strategy, and Idle/Clicker — plus support for user-created
  custom categories.
- Auto-sort suggestions by keyword and by BBS tag, including
  **suggest-new-category** clustering (by theme and by author) once enough
  unsorted entries share a pattern.

### Data safety
- **PICO-8 category-strip recovery**: PICO-8 itself rewrites
  `favourites.txt` and strips all category headers whenever a new favourite
  is saved in-game. This app detects that condition on load and
  reconstructs categories from (in order of preference) a persistent
  master record, then rotating on-disk backups — never silently discarding
  your organization.
- **Persistent master-category record** (`favourites.txt.master.json`):
  an append-only, portable history of every slug's last-known category,
  independent of the live favourites file. Exportable/importable for
  moving your organization between devices.
- **Duplicate detection**: same-cart-ID revision groups and
  same-author/near-identical-title groups across different cart IDs, with a
  dedicated scrollable review screen. Nothing is auto-deleted — fuzzy
  author/title matches are surfaced for manual review only.
- **Reload from disk** (discard in-app changes) and safe category
  rename/delete that immediately updates the master record so a PICO-8
  strip can't resurrect a just-deleted category.
- Identity-based (not value-based) list removal throughout, to prevent
  duplicate-entry data loss during moves and dedup operations.
- Boot-time and runtime crash logging to `/tmp/pico8sorter_crash.log`
  (SDL init, window/renderer creation, font loading, and the main input
  loop are all wrapped so a failure is recorded instead of dying silently).

### Input handling
- Raw SDL `SDL_Joystick` API (not the SDL GameController API), since muOS
  only populates `gamecontrollerdb.txt` for emulator launches, not
  standalone apps.
- Full RG CubeXX-H button map, including L2/R2 as digital buttons
  (`b13`/`b14`), not analog triggers.
- Controls:
  - D-pad — navigate
  - A — confirm
  - B — back
  - X — action menu (find duplicates, export/import master list, reload,
    etc.)
  - Y — toggle / sort
  - L1 / R1 — page scroll
  - L2 / R2 — move entry within a category / reorder categories
  - START — save
  - SELECT — quit

---

## Installation (muOS)

1. Copy the app folder to
   `/run/muos/storage/application/Pico8FavsSorter` (exact casing required).
2. Ensure `mux_launch.sh` is present alongside `main.py` — muOS reads its
   `# HELP`, `# ICON`, and `# GRID` metadata directly from the launcher's
   comment lines.
3. Launch from the muOS Applications section.

If the app fails to boot, check `/tmp/pico8sorter_crash.log` first — every
startup step (SDL init, window, renderer, fonts, favourites-file load) logs
its failure there before exiting.

---

## Credits & References

- **DinguxCommander** (leonkasovan) — referenced as an SDL2/`ctypes`
  reference implementation for raw-joystick input handling patterns on
  handheld Linux devices.
- **MustardOS** (github.com/MustardOS) — target OS; device SDL button
  mappings sourced from the MustardOS/internal device config for the
  RG CubeXX-H.
- PICO-8 and the Lexaloffle BBS are products of Lexaloffle Games. This
  project is an independent, unofficial utility and is not affiliated
  with or endorsed by Lexaloffle Games.

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file
(or add one to the repo) for the full text — you're free to use, copy,
modify, merge, publish, distribute, sublicense, and sell copies, provided
the copyright notice is retained. Provided "as is," with no warranty.

### A note on originality

The `favourites.txt` parsing, category-header reconstruction, and
persistent master-category recovery system (the logic that detects and
repairs PICO-8's own habit of stripping category headers when it rewrites
the file) is original work created for this project. It is not derived
from, or part of, PICO-8 itself — it's a third-party tool that reads and
writes PICO-8's favourites file format. `favourites.txt`'s file *format*
is defined by PICO-8/Lexaloffle and is not itself covered by this
project's license; only the code in this repository (the parser,
reconstruction logic, UI, and related tooling) is MIT-licensed.

Replace `[Kaleb]` above with your preferred name or handle before
publishing.
