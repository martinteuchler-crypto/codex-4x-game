from random import Random

from game.core import ai, mapgen
from game.core.models import Player, State


def make_state() -> State:
    tiles, spawns = mapgen.generate_map(5, 5, seed=2)
    units = {u.id: u for u in mapgen.initial_units(spawns)}
    players = {0: Player(0), 1: Player(1)}
    state = State(5, 5, tiles, units, {}, players)
    state.next_unit_id = max(units) + 1
    state.current_player = 1
    return state


def test_ai_expands():
    state = make_state()
    rng = Random(0)
    for _ in range(5):
        ai.ai_turn(state, rng)
    assert state.cities or any(
        u.owner == 1 and u.pos != (state.width - 2, state.height - 2)
        for u in state.units.values()
    )
