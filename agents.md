# agents.md — Space 4X with R\&D (Research & Tech Tree) using Pygame

This spec instructs a code-generating agent to build a small but extensible **space 4X** prototype with a lightweight **Research & Development (R\&D)** system and a **mini tech tree**. Stack: **Python 3.11**, **pygame**, **pygame\_gui**, **dataclasses**, **typing**. No networking.

---

## 0) TL;DR for the Agent

* **Goal:** Playable local space-4X with exploration, colonies, starbases, ships, fog-of-war, basic combat **plus** research that unlocks units and passive bonuses.
* **Deliverables:**

  1. Runnable game: `python -m game.main` (menu → new game → playable starmap).
  2. Deterministic tests for rules/AI/research.
  3. Save/Load JSON (including research state).
  4. Lint/format via ruff/black; README with instructions.
* **Non-goals:** diplomacy, trade, complex ship design.

---

## 1) Repository Layout

```
.
├─ README.md
├─ agents.md
├─ pyproject.toml
├─ requirements.txt
├─ game/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ core/
│  │  ├─ models.py
│  │  ├─ rules.py
│  │  ├─ mapgen.py
│  │  ├─ saveio.py
│  │  ├─ ai.py
│  │  └─ tech.py           # NEW: tech tree + research logic
│  ├─ ui/
│  │  ├─ renderer.py
│  │  ├─ hud.py
│  │  └─ input.py
│  └─ scenes/
│     ├─ menu.py
│     └─ gameplay.py
└─ tests/
   ├─ test_rules.py
   ├─ test_ai.py
   ├─ test_saveio.py
   └─ test_research.py     # NEW: research unit tests
```

---

## 2) Game Design (Space Theme MVP + R\&D)

### Core Concepts

* **Starmap:** Grid (20×12 default). Sector kinds: `deep_space`, `asteroids`, `nebula`, `star`. Some sectors host a **habitable planet** (for colonies).
* **Fog of War / Sensors:** Ships and structures reveal sectors within `sensor_range`.
* **Starts:** Each player begins with a **home colony** (on a habitable planet) and a **Scout Ship** in a nearby sector.
* **Structures:**

  * **Colony** (on habitable planet): generates **credits**, **metal**, and **research**.
  * **Starbase** (adjacent sector, not `star`/`nebula`): extends sensors, repairs, and can build ships.
* **Ships:**

  * **Scout Ship** — fast, explores; available at start.
  * **Starship** — combat ship; **locked** behind tech until researched.
  * **Colony Ship** — founds new colony on habitable planet; **locked** behind tech until researched.
* **Economy:** Global per player: **credits**, **metal**, **research** (RPs) gained each **End Turn** from colonies/starbases and tech bonuses.
* **Combat:** Simple autoresolve on contact; starship captures colonies and destroys starbases.

### Research & Tech Tree (Mini)

* Players accumulate **Research Points (RP)** each turn.
* RP can be allocated to **one active technology at a time** (MVP). Overflow carries over.
* When RP ≥ tech cost → tech **unlocks** and its effect applies immediately.
* **Mini Tree (IDs, names, costs, effects):**

  * `T1_PROPULSION` — **Basic Propulsion** (Cost: 20 RP)

    * +1 moves to **Scout** and **Colony Ship**.
  * `T1_MINING` — **Asteroid Extraction** (Cost: 20 RP)

    * +1 metal yield from `asteroids` adjacent to any friendly colony/starbase.
  * `T1_SENSORS` — **Enhanced Sensors** (Cost: 20 RP)

    * +1 sensor range for ships and starbases.
  * `T2_CONSTRUCTION` — **Orbital Construction** (Cost: 35 RP) — **requires any one T1**

    * Unlock **Starbases** building at colonies; starbase build cost −1 metal.
  * `T2_COLONIZATION` — **Deep-Space Colonization** (Cost: 35 RP) — **requires any one T1**

    * Unlock **Colony Ship**.
  * `T2_WEAPONRY` — **Coilguns** (Cost: 35 RP) — **requires any one T1**

    * Unlock **Starship**; starships move +1 in `deep_space`.

> MVP rule-of-thumb: T1 can be researched in \~6–10 turns; T2 in \~10–15 from start, depending on map yields.

---

## 3) Data Model (in `models.py`)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Coord = Tuple[int, int]

@dataclass
class Tile:
    x: int
    y: int
    kind: str            # 'deep_space'|'asteroids'|'nebula'|'star'
    habitable: bool = False
    revealed_by: Set[int] = field(default_factory=set)

@dataclass
class Unit:
    id: int
    owner: int           # 0 human, 1 ai
    kind: str            # 'scout'|'starship'|'colony_ship'
    pos: Coord
    moves_left: int

@dataclass
class City:              # role distinguishes colony/starbase
    id: int
    owner: int
    pos: Coord
    role: str            # 'colony'|'starbase'

@dataclass
class Player:
    id: int
    credits: int = 0
    metal: int = 0
    research: int = 0              # RP available (unspent)
    tech_unlocked: Set[str] = field(default_factory=set)
    tech_progress: Dict[str, int] = field(default_factory=dict)  # RP toward current tech
    active_tech: Optional[str] = None
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
    seed: int = 0
```

---

## 4) Configuration (`config.py`)

```python
TILE_SIZE = 32
UI_BAR_H = 64
MOVE_COST = {"deep_space":1, "asteroids":2, "nebula":2, "star":999}
BASE_YIELD = {"deep_space": (0,0,0), "asteroids": (0,2,0), "nebula": (1,0,1), "star": (1,1,1)}  # (credits, metal, research)
COLONY_YIELD_BONUS = (2,1,1)  # added for colonies on habitable
UNIT_STATS = {
    "scout": {"moves": 4, "sensor": 3, "cost": {"credits": 2, "metal": 1}},
    "starship": {"moves": 3, "sensor": 2, "cost": {"credits": 4, "metal": 3}},
    "colony_ship": {"moves": 3, "sensor": 2, "cost": {"credits": 3, "metal": 3}},
}
STRUCTURE_STATS = {
    "starbase": {"sensor": 3, "cost": {"credits": 2, "metal": 4}},
}
REVEAL_RADIUS = 3
START_SIZE = (20, 12)

# --- Tech tree definitions ---
TECH_DEFS = {
    "T1_PROPULSION": {
        "name": "Basic Propulsion",
        "tier": 1,
        "cost": 20,
        "requires": [],
        "effects": {"unit_moves+": {"scout": 1, "colony_ship": 1}},
    },
    "T1_MINING": {
        "name": "Asteroid Extraction",
        "tier": 1,
        "cost": 20,
        "requires": [],
        "effects": {"yield_bonus": {"asteroids": {"metal": 1}}},
    },
    "T1_SENSORS": {
        "name": "Enhanced Sensors",
        "tier": 1,
        "cost": 20,
        "requires": [],
        "effects": {"sensor+": 1},
    },
    "T2_CONSTRUCTION": {
        "name": "Orbital Construction",
        "tier": 2,
        "cost": 35,
        "requires": ["any:T1"],
        "effects": {"unlock": ["starbase"], "build_cost-": {"starbase": {"metal": 1}}},
    },
    "T2_COLONIZATION": {
        "name": "Deep-Space Colonization",
        "tier": 2,
        "cost": 35,
        "requires": ["any:T1"],
        "effects": {"unlock": ["colony_ship"]},
    },
    "T2_WEAPONRY": {
        "name": "Coilguns",
        "tier": 2,
        "cost": 35,
        "requires": ["any:T1"],
        "effects": {"unlock": ["starship"], "terrain_move_bonus": {"deep_space": {"starship": 1}}},
    },
}
```

---

## 5) Tech System (`core/tech.py`)

Implement pure helpers the rules/hud can call.

**Public API:**

* `get_research_income(state: State, player_id: int) -> int` — compute RP income from colonies (BASE\_YIELD + COLONY\_YIELD\_BONUS + tech effects).
* `can_research(player: Player, tech_id: str) -> tuple[bool, str]` — checks requirements (`requires` supports `any:T1`).
* `apply_research_income(state: State, player_id: int) -> State` — add RP into `active_tech` progress, unlock on completion.
* `unlock_tech(state: State, player_id: int, tech_id: str) -> State` — adds to `tech_unlocked` and applies **passive effects cache** (e.g., sensor/move bonuses) stored in `player.tech_bonuses` (extend `Player` if you prefer), or compute effects on the fly from `tech_unlocked` in rules.
* `list_researchable(player: Player) -> list[str]` — return techs that pass `can_research` and are not unlocked.

**Effects semantics:**

* `unlock`: allows building the unit/structure.
* `unit_moves+`: additive to base moves of specific units.
* `sensor+`: additive to all sensors (units/starbases owned by that player).
* `yield_bonus`: per-sector-kind flat addition near friendly presence when tallying end-of-turn income.
* `build_cost-`: reduces metal/credit costs when building at colonies/starbases.
* `terrain_move_bonus`: when entering that terrain, reduce move cost by N for listed unit kinds (min 1).

Keep effects **owner-scoped** and applied only for that player.

---

## 6) Actions & Rules (`core/rules.py`)

Extend MVP with R\&D hooks.

**Public API (pure functions returning new `State`):**

* `start_game(seed:int, w:int, h:int) -> State`
* `end_turn(state: State) -> State`

  1. Tally income (credits/metal/RP) with tech effects,
  2. Apply research income (progress active tech, unlock if done),
  3. Reset moves/repairs,
  4. If next player is AI → `ai_take_turn`.
* Movement / combat as before; recompute sensors after movement/build.
* **Build APIs:** `build_unit(state, base_id, kind)`, `build_starbase(state, colony_id, to)` (check `unlock` via tech), `found_colony(state, unit_id)`.
* **Research APIs:** `set_active_tech(state, player_id, tech_id)` (validate via `can_research`), `clear_active_tech(state, player_id)`.

**Validation notes:**

* Cannot build **starship/colony\_ship/starbase** until unlocked.
* Costs after `build_cost-` must not drop below zero.
* Sensors/moves incorporate tech bonuses at compute time.

---

## 7) Map Generation (`core/mapgen.py`)

* Generate starfield clusters and \~10–15% habitable sectors.
* Ensure both players start with a **home colony** on a habitable sector and a **scout** nearby.

---

## 8) UI (`ui/hud.py`, `ui/renderer.py`)

Add an **R\&D panel**:

* **Research dropdown/list**: shows current `active_tech` progress like `Basic Propulsion (12/20 RP)`.
* **Buttons**: `Set Active` (on selected tech), `Clear` (no active research), and build buttons disabled until their tech is unlocked.
* Tooltips explaining effects and prerequisites.
* Optional **Tech Overlay**: small modal with the mini tree and arrows (T1 → T2).

Renderer notes: keep visuals minimal (glyphs for star/nebula/asteroids; planet dots around stars). Highlight colonies/starbases. Show sensor rings on hover if helpful.

---

## 9) AI (`core/ai.py`)

* If `T2_COLONIZATION` not unlocked and affordable → prefer researching it; else if no offensive capability, pick `T2_WEAPONRY`; else `T1_*` that maximizes near-term movement/sensor.
* Spend RP automatically via `end_turn` → `apply_research_income`.
* Build priorities: early **scout**, then **colony\_ship** once unlocked, then **starship**.
* Tactical: attack adjacent enemies; otherwise BFS toward nearest unrevealed/habitable.

---

## 10) Save/Load (`core/saveio.py`)

* Include `players[*].research`, `tech_unlocked`, `tech_progress`, `active_tech`.
* `schema_version: 2` (since R\&D added).

---

## 11) Tests (`tests/`)

* `test_research.py`:

  * Research income accrues from colonies and applies to `active_tech`.
  * Unlock fires exactly when `progress >= cost`; effects apply (e.g., build unlocks, move/sensor increase).
  * `list_researchable` respects prerequisites `any:T1`.
* `test_rules.py` additions:

  * Cannot build locked units/structures pre-tech.
  * Costs reflect `build_cost-` after `T2_CONSTRUCTION`.
* `test_ai.py` additions:

  * Given a seeded map and income, AI eventually unlocks a T2 and builds the corresponding unit.

---

## 12) Prompts for the Code Agent

Use these prompts to synthesize files.

**(a) tech.py**

> Create `game/core/tech.py` implementing TECH\_DEFS from `config.py`, with helpers `can_research`, `list_researchable`, `get_research_income`, `apply_research_income`, `unlock_tech`. Effects should be computed owner-scoped. Keep functions pure and testable; no pygame imports.

**(b) rules.py (research hooks)**

> Update `game/core/rules.py` to integrate research: income tally includes BASE\_YIELD, COLONY\_YIELD\_BONUS, and tech yield bonuses; `end_turn` applies research progression and unlocks; validate build actions against `unlock` effects; movement and sensors should consider tech bonuses from unlocked techs.

**(c) hud.py (R\&D UI)**

> Add an R\&D panel with a dropdown of researchable techs, a progress bar for `active_tech`, and buttons to set/clear active research. Disable build buttons until tech unlocks.

**(d) tests/test\_research.py**

> Add unit tests covering research accrual, unlocking thresholds, prerequisite logic, and effect application (unlocking starship/colony\_ship, sensor/move bonuses, build cost reductions).

---

## 13) Acceptance Criteria (with R\&D)

1. **Start:** Human starts with home colony (on habitable), a scout, and **no T2 techs unlocked**.
2. **Research Loop:** Each End Turn increases RP, applies to chosen tech, and unlocks when cost met.
3. **Locks/Unlocks:** Starbase, Colony Ship, and Starship cannot be built until their tech is unlocked; immediately possible after unlocking.
4. **Effects:** Propulsion/Sensors/Mining bonuses visibly affect movement, sensor rings, and income in the very next turn.
5. **UI:** R\&D panel shows current active tech and progress; can switch active tech.
6. **Save/Load:** Preserves research fields; reload continues with same tech progress and effects.
7. **Tests:** `pytest -q` passes including `test_research.py`.

---

## 14) Stretch Ideas (optional)

* Multiple concurrent research slots with split allocation.
* Tech events (random breakthroughs) tied to nebula exploration.
* Mini ship-upgrade mods unlocked by techs.
