"""Gameplay rules such as movement and turn handling."""

from __future__ import annotations

from typing import Tuple

from .models import State
from ..config import MOVE_COST, UNIT_STATS
from .tech import apply_research_income

Coord = Tuple[int, int]


def get_tile(state: State, pos: Coord):
    return next(t for t in state.tiles if (t.x, t.y) == pos)


def move_unit(state: State, unit_id: int, dest: Coord) -> bool:
    unit = state.units[unit_id]
    cost = MOVE_COST[get_tile(state, dest).kind]
    if unit.moves_left >= cost:
        unit.pos = dest
        unit.moves_left -= cost
        return True
    return False


def end_turn(state: State) -> State:
    # Refresh moves
    for unit in state.units.values():
        unit.moves_left = UNIT_STATS[unit.kind]["moves"]
    # Apply research income for current player
    apply_research_income(state, state.current_player)
    # Switch player
    state.current_player = 1 - state.current_player
    state.turn += 1
    return state
