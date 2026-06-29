# PICO-8 Favourites Sorter — muOS Edition (v1.3.2)

A lightweight, standalone Python 3 utility featuring a custom graphical user interface (GUI) designed to organize, filter, and categorize your PICO-8 Splore favorites. Optimized explicitly for the **Anbernic RG Cube XX** (720×720 screen resolution) running **MustardOS / muOS**.

Built using pure Python 3 and standard `SDL2` via `ctypes`. **No external packages, no `pip install`, and no dependencies required.**

---

## 🕹️ Controls

The interface relies entirely on raw hardware inputs mapped directly from the device's native controller configuration:

| Input | Left Panel Action | Category Panel Action | Right Panel Action |
| :--- | :--- | :--- | :--- |
| **D-Pad Up / Down** | Navigate entries | Navigate categories | Navigate entries |
| **D-Pad Left / Right**| Switch focus panels | Switch focus panels | Switch focus panels |
| **A** | Select game to assign | Confirm category assignment | Open Category |
| **B** | Clear selection / Cancel | Cancel assignment | Back to panel focus |
| **X** | Open Action Menu | Open Action Menu | Open Action Menu |
| **Y** | Toggle `UNSORTED` ↔ `ALL` | N/A | Sort Category (A → Z) |
| **L1 / R1** | Page Up / Down | Page Up / Down | Page Up / Down |
| **L2 / R2** | N/A | Move selected category Up / Down | Move entry Up / Down inside category |
| **START** | Save changes immediately | Save changes immediately | Save changes immediately |
| **SELECT** | Quit tool to muOS dashboard | Quit tool to muOS dashboard | Quit tool to muOS dashboard |

---

## ✨ Features

* **Zero-Dependency Core:** Runs smoothly out of the box using built-in Python library wrappers for SDL2.
* **Dual Filtering Modes:** Toggle smoothly between checking only your `NEW/UNSORTED` carts or viewing `ALL ENTRIES`.
* **Advanced Sorting Engine:** Instantly cycle through sorting lists globally by Title, Author, or Category. 
* **Dynamic Category Reordering:** Manage layout ordering by pressing `L2`/`R2` directly in the Category column to shift section placements on your next save.
* **Robust File-Safety Guardrails:**
  * **Atomically-Safe Overwrites:** Writes directly to a secondary

 ---

## 🍓 Also Available for Raspberry Pi OS

If you're sorting PICO-8 favourites on a **Raspberry Pi**, check out the companion project:

👉 [pico8-fav-sorter](https://github.com/PuppetHoundZ/pico8-fav-sorter) — GTK3 GUI favourites sorter for Raspberry Pi OS with BBS tag enrichment, auto-sorting, and touchscreen support
