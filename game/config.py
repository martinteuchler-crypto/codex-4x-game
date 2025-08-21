"""Game configuration constants."""

TILE_SIZE = 32
UI_BAR_H = 64
MOVE_COST = {"deep_space": 1, "asteroids": 2, "nebula": 2, "star": 999}
BASE_YIELD = {
    "deep_space": (0, 0, 0),
    "asteroids": (0, 2, 0),
    "nebula": (1, 0, 1),
    "star": (1, 1, 1),
}
COLONY_YIELD_BONUS = (2, 1, 1)
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
        "effects": {
            "unlock": ["starship"],
            "terrain_move_bonus": {"deep_space": {"starship": 1}},
        },
    },
}
