"""Very simple AI for expansion/attack."""

from __future__ import annotations

from random import Random
from typing import List

from .models import Coord, State
from .rules import RuleError, end_turn, found_city, move_unit

DIRS: List[Coord] = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def ai_turn(state: State, rng: Random) -> None:
    """Perform a simple AI turn."""
    for unit in list(state.units.values()):
        if unit.owner != state.current_player:
            continue
        for _ in range(4):
            dx, dy = rng.choice(DIRS)
            dest = (unit.pos[0] + dx, unit.pos[1] + dy)
            try:
                move_unit(state, unit.id, dest)
                return
            except RuleError:
                continue
        try:
            found_city(state, unit.id, rng)
            return
        except RuleError:
            continue
    end_turn(state)


__all__ = ["ai_turn"]
