# agents.md — 4X (Explore/Expand/Exploit/Exterminate) Game with Pygame

This document tells a code-generating agent exactly what to build and how to structure the repo for a small but extensible **4X** game using **Python 3.11**, **pygame**, and **pygame\_gui**. Tkinter may be used only for a launcher dialog (optional).

---

## 0) TL;DR for the Agent

* **Goal:** Ship a playable local 4X prototype within one session. Core loop: fog-of-war exploration, founding cities, simple resource income per turn, and basic combat between units.
* **Stack:** Python 3.11, pygame, pygame\_gui, dataclasses, typing. No network.
* **Deliverables:**

  1. Runnable game (`python -m game.main`) with menu → new game → playable map.
  2. Deterministic headless tests for rules/AI.
  3. Save/load JSON for game state.
  4. Lint/format CI (ruff/black) and instructions in README.
* **Non-goals (MVP):** No fancy graphics, no multiplayer, no persistence beyond JSON files.

---

## 1) Repository Layout

```
.
├─ README.md
├─ agents.md                     # this file
├─ pyproject.toml                # ruff/black + project metadata
├─ requirements.txt              # pygame, pygame_gui
├─ game/
│  ├─ __init__.py
│  ├─ main.py                    # entry point; pygame loop & scene router
│  ├─ config.py                  # constants and tunables
│  ├─ core/
│  │  ├─ rules.py                # turn engine, actions, validation, RNG
│  │  ├─ models.py               # dataclasses for State, Unit, City, Tile
│  │  ├─ mapgen.py               # procedural map, fog, resources
│  │  ├─ saveio.py               # JSON save/load (schema below)
│  │  └─ ai.py                   # simple AI (greedy expand/attack)
│  ├─ ui/
│  │  ├─ renderer.py             # draw map/units; camera; layers
│  │  ├─ hud.py                  # buttons, panels, tooltips via pygame_gui
│  │  └─ input.py                # translate mouse/keyboard → game actions
│  └─ scenes/
│     ├─ menu.py                 # main menu
│     └─ gameplay.py             # running game scene
└─ tests/
   ├─ test_rules.py
   ├─ test_ai.py
   └─ test_saveio.py
```

---

## 2) Coding Standards

* Use **type hints** and **dataclasses**. Run **ruff** and **black** (config in `pyproject.toml`).
* No global state. All randomness flows from `Random(seed)` in `rules.py` so tests are deterministic.
* Rendering is a thin layer; game logic is pure and testable.
* Functions < 60 lines when possible. Prefer composition over inheritance.
* Separate **Intent** (player clicks) from **Action** (validated game operation).

---

## 3) Game Design (MVP)

### Core Concepts

* **Map:** Rect grid (20×12 default). Tiles: `plains`, `forest`, `hill`, `water`. Each has move cost and yield.
* **Fog of War:** Tiles start hidden; units reveal in radius 3.
* **Units:** `Scout` (fast, weak), `Soldier` (slow, fights), both 1 HP for MVP. Movement points per turn.
* **Cities:** Founded on revealed land; produce **food** and **production** each turn.
* **Resources & Economy:** Each city yields `food=1..3`, `prod=1..2` depending on adjacent tiles; global per player. Production buys new units at city locations.
* **Turns:** Players alternate; AI is Player 2.
* **Combat:** If a unit enters an enemy unit’s tile, the attacker wins (MVP rule) and defender is removed. City capture if attacked with Soldier.

### Win/Lose

* Win: Opponent has **no cities**. Lose: Player has **no cities**.

### UX

* Left-click to select; right-click to move. Buttons: End Turn, Found City, Buy Unit (Soldier/Scout) if at city and enough production.
* HUD shows: current player, turn number, resources, selected unit info.

---

## 4) Data Model (in `models.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

Coord = Tuple[int, int]

@dataclass
class Tile:
    x: int
    y: int
    kind: str              # 'plains' | 'forest' | 'hill' | 'water'
    revealed_by: set[int] = field(default_factory=set)

@dataclass
class Unit:
    id: int
    owner: int             # 0 human, 1 ai
    kind: str              # 'scout' | 'soldier'
    pos: Coord
    moves_left: int

@dataclass
class City:
    id: int
    owner: int
    pos: Coord

@dataclass
class Player:
    id: int
    production: int = 0
    food: int = 0
    units: List[int] = field(default_factory=list)
    cities: List[int] = field(default_factory=list)

@dataclass
class State:
    width: int
    height: int
    tiles: List[Tile]
    units: Dict[int, Unit]
    cities: Dict[int, City]
    players: Dict[int, Player]
    current_player: int
    turn: int
    next_unit_id: int = 1
    next_city_id: int = 1
```

---

## 5) Actions & Rules (in `rules.py`)

* Public API (pure functions that return **new** `State` and/or `events`):

  * `start_game(seed:int, w:int, h:int) -> State`
  * `end_turn(state: State) -> State`
  * `select_unit(state, unit_id)` (UI-level only)
  * `move_unit(state, unit_id, to: Coord) -> State`
  * `found_city(state, unit_id) -> State`
  * `buy_unit(state, city_id, kind: str) -> State`
* **Validation**: Actions raise `RuleError` with strings safe to show in UI.
* **RNG**: All randomness uses a `Random` created from `state.turn` + `seed` stored in `State`.

---

## 6) Map Generation (`mapgen.py`)

* Inputs: `w, h, seed`.
* Algorithm: simple midpoint-ish noise or cellular rules to place `water`, then scatter `forest` and `hill`.
* Guarantee: each player starts on a land tile with at least 4 land neighbors.
* Provide `initial_units`: each player gets one `Scout` at spawn; Player 0 also gets a `Soldier`.

---

## 7) Save/Load (`saveio.py`)

* `save_game(state: State, path: str) -> None` (JSON, versioned schema)
* `load_game(path: str) -> State`
* Include `schema_version: 1` and compress lists for tiles and units for size.

---

## 8) Scenes & Loop

* `menu.py`: buttons for **New Game**, **Load Game**, **Quit**. New Game asks map size and seed.
* `gameplay.py`: main loop calls `rules` and `renderer`/`hud`.
* ESC → pause menu with **Save**/**Exit to Menu**.

---

## 9) UI Layer Contracts

* `renderer.draw(state, screen, camera)` draws tiles, units, city markers, and minimal overlays.
* `hud.build(manager)` returns a struct with references to buttons/labels; events are dispatched via `pygame_gui`.
* `input.translate(event, state)` yields **intents**: `Select(pos)`, `Move(to)`, `FoundCity`, `EndTurn`, `Buy(kind)`.

---

## 10) AI (`ai.py`)

* Deterministic, greedy:

  * If enemy adjacent → move to attack.
  * Else if visible city tile adjacent → capture.
  * Else prefer moving towards nearest unrevealed tile.
  * If enough production at turn start → buy Scout.
* One function: `ai_take_turn(state: State) -> State`.

---

## 11) Tests (pytest)

* `test_rules.py`: movement costs, fog reveal radius, city founding validation, buy unit costs, win condition.
* `test_ai.py`: given a seeded map, AI expands in ≤ N turns.
* `test_saveio.py`: round-trip save/load equals original (ignoring computed caches).

---

## 12) Configuration (`config.py`)

```python
TILE_SIZE = 32
UI_BAR_H = 64
MOVE_COST = {"plains":1, "forest":2, "hill":2, "water":999}
YIELD = {"plains": (1,1), "forest": (0,2), "hill": (0,2), "water": (0,0)}  # (food, prod)
UNIT_STATS = {"scout": {"moves":3, "cost":3}, "soldier": {"moves":2, "cost":4}}
REVEAL_RADIUS = 3
START_SIZE = (20, 12)
```

---

## 13) Build & Run

* `requirements.txt`: `pygame>=2.5.0`, `pygame_gui>=0.6.9`, `pytest`, `black`, `ruff`.
* Run: `python -m game.main`
* Tests: `pytest -q`
* Format/lint: `ruff check . && black .`

---

## 14) Prompts for the Code Agent

Use these structured prompts to generate specific parts. Replace `<<<...>>>` where appropriate.

### 14.1 Generate Data Models

> You are a Python game dev assistant. Create `game/core/models.py` implementing the dataclasses and types defined in section 4 of `agents.md`. Include `__all__` and type hints. No I/O. Make it PEP8 compliant and under 200 lines.

### 14.2 Implement Rules

> Implement `game/core/rules.py` as specified in sections 5 and 12: pure functions, deterministic RNG, and validation via `RuleError(Exception)`. Provide movement, founding cities, buying units, fog reveal, win check, end\_turn.

### 14.3 Map Generation

> Implement `game/core/mapgen.py` to produce a connected landmass and fair spawns using seed. Expose `generate_map(w,h,seed) -> tuple[tiles, spawns]` and `initial_units(spawns) -> list[Unit]`.

### 14.4 UI & Loop

> Create `game/ui/renderer.py`, `game/ui/hud.py`, `game/ui/input.py`, and `game/scenes/gameplay.py` to render grid, handle input intents, and wire to rules. Use `pygame_gui` for buttons (End Turn, Found City, Buy Scout, Buy Soldier). Keep code < 250 lines per file.

### 14.5 Menu Scene

> Implement `game/scenes/menu.py` with New/Load/Quit. New launches `gameplay.py` with chosen size/seed. Add `game/main.py` scene router and top-level `pygame` initialization.

### 14.6 Save/Load

> Implement `game/core/saveio.py` with `save_game(state, path)` and `load_game(path)` JSON schema v1. Avoid circular refs by storing IDs.

### 14.7 Tests

> Write `tests/test_rules.py`, `tests/test_ai.py`, and `tests/test_saveio.py` per section 11. Use a fixed seed. Do not import pygame in tests.

---

## 15) Acceptance Criteria (Agent must satisfy)

1. **Launch:** `python -m game.main` opens menu in a window. New Game produces a playable map in ≤ 2s.
2. **Turns:** End Turn increments turn and switches current player. AI performs an action within 1s.
3. **Movement & Fog:** Moving reveals tiles with radius=3 and respects terrain costs.
4. **Found City:** Only on revealed, non-water tiles; creates city; resources update on End Turn.
5. **Buy Unit:** From a city, spend production to create unit at city tile; cannot over-spawn on the same tile if occupied by enemy.
6. **Combat:** Entering enemy unit tile removes defender; entering enemy city with Soldier transfers ownership.
7. **Save/Load:** From pause menu, saving to JSON and loading restores the same state (tested).
8. **Tests pass:** `pytest -q` reports green on CI and locally.

---

## 16) Stretch Goals (if time allows)

* Animated movement and simple combat effects.
* City growth: food surplus grows population → extra yields.
* Tech tree with 3 nodes affecting yields or unit stats.
* Map preview/minimap.

---

## 17) Known Pitfalls & Constraints for the Agent

* Do **not** run Tkinter and pygame event loops simultaneously; if a Tk launcher is added, it must close before starting the game.
* Avoid nondeterministic RNG in rules and AI—tests rely on reproducibility.
* Keep UI threads single-threaded; no multiprocessing needed.
* Ensure window resizing doesn’t break rendering or input hit-tests.

---

## 18) Glossary for the Agent

* **Intent:** UI-level request (e.g., user clicked a tile) that may or may not be valid.
* **Action:** Validated state transition (e.g., `move_unit`).
* **State:** Entire game world; immutable return semantics preferred (may mutate in place if simpler, but ensure tests treat state as authoritative single source of truth).

---

## 19) Checklist Before You Finish

* [ ] Repo layout matches section 1.
* [ ] Game boots, plays, and exits cleanly.
* [ ] JSON save/load round-trips.
* [ ] All tests green.
* [ ] README contains run/test instructions and screenshot key bindings.
* [ ] Code passes `ruff` and `black`.