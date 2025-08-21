"""Very lightweight AI for testing."""

from __future__ import annotations

import random

from .models import State
from .rules import move_unit


def take_turn(state: State, player_id: int, seed: int | None = None) -> State:
    rng = random.Random(seed or state.seed)
    player = state.players[player_id]
    for uid in player.units:
        unit = state.units[uid]
        # Try moving randomly within bounds
        dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        dest = (
            max(0, min(state.width - 1, unit.pos[0] + dx)),
            max(0, min(state.height - 1, unit.pos[1] + dy)),
        )
        move_unit(state, uid, dest)
    return state
