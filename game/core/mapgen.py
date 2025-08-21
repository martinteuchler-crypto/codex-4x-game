"""Map generation utilities."""

from __future__ import annotations

import random
from typing import List

from .models import City, Player, State, Tile, Unit
from ..config import START_SIZE, UNIT_STATS

TERRAIN = ["deep_space", "asteroids", "nebula", "star"]


def generate_state(
    width: int | None = None, height: int | None = None, seed: int = 0
) -> State:
    width = width or START_SIZE[0]
    height = height or START_SIZE[1]
    rng = random.Random(seed)

    tiles: List[Tile] = []
    for y in range(height):
        for x in range(width):
            kind = rng.choice(TERRAIN)
            habitable = kind == "star" and rng.random() < 0.3
            tiles.append(Tile(x, y, kind, habitable))

    state = State(
        width=width,
        height=height,
        tiles=tiles,
        units={},
        cities={},
        players={0: Player(id=0), 1: Player(id=1)},
        current_player=0,
        turn=1,
        seed=seed,
    )

    # Place home colony for player 0 at center
    home_pos = (width // 2, height // 2)
    colony = City(id=state.next_city_id, owner=0, pos=home_pos, role="colony")
    state.cities[colony.id] = colony
    state.players[0].cities.append(colony.id)
    state.next_city_id += 1

    # Place scout unit for player 0
    scout = Unit(
        id=state.next_unit_id,
        owner=0,
        kind="scout",
        pos=(home_pos[0] + 1, home_pos[1]),
        moves_left=UNIT_STATS["scout"]["moves"],
    )
    state.units[scout.id] = scout
    state.players[0].units.append(scout.id)
    state.next_unit_id += 1

    # AI home colony and scout at opposite corner
    ai_home = (1, 1)
    colony2 = City(id=state.next_city_id, owner=1, pos=ai_home, role="colony")
    state.cities[colony2.id] = colony2
    state.players[1].cities.append(colony2.id)
    state.next_city_id += 1

    scout2 = Unit(
        id=state.next_unit_id,
        owner=1,
        kind="scout",
        pos=(ai_home[0] + 1, ai_home[1]),
        moves_left=UNIT_STATS["scout"]["moves"],
    )
    state.units[scout2.id] = scout2
    state.players[1].units.append(scout2.id)
    state.next_unit_id += 1

    return state
