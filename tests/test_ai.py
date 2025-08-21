from random import Random

from game.core import ai, rules


def test_ai_moves() -> None:
    state = rules.new_game(6, 6, seed=1)
    rng = Random(1)
    # ensure clear surroundings
    spawn = (state.width - 2, state.height - 2)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (spawn[0] + dx, spawn[1] + dy) in state.tiles:
                state.tiles[(spawn[0] + dx, spawn[1] + dy)].kind = "plains"
    ai.ai_take_turn(state, rng)
    moved = any(u.owner == 1 and u.pos != spawn for u in state.units.values())
    has_city = any(c.owner == 1 for c in state.cities.values())
    assert moved or has_city
