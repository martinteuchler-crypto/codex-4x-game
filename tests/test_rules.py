import pytest

from game import config
from game.core import rules
from game.core.models import State


def setup_state() -> State:
    state = rules.new_game(4, 4, seed=0)
    return state


def test_move_cost() -> None:
    state = setup_state()
    unit = next(iter(state.units.values()))
    # set destination to water so cost high
    dest = (unit.pos[0] + 1, unit.pos[1])
    state.tiles[dest].kind = "forest"
    unit.moves_left = 1
    with pytest.raises(rules.RuleError):
        rules.move_unit(state, unit.id, dest)


def test_reveal_radius() -> None:
    state = setup_state()
    unit = next(iter(state.units.values()))
    dest = (unit.pos[0] + 1, unit.pos[1])
    state.tiles[dest].kind = "plains"
    rules.move_unit(state, unit.id, dest)
    px, py = dest
    for dy in range(-config.REVEAL_RADIUS, config.REVEAL_RADIUS + 1):
        for dx in range(-config.REVEAL_RADIUS, config.REVEAL_RADIUS + 1):
            tile = (px + dx, py + dy)
            if tile in state.tiles:
                assert unit.owner in state.tiles[tile].revealed_by


def test_found_city_validation() -> None:
    state = setup_state()
    unit = next(iter(state.units.values()))
    state.tiles[unit.pos].kind = "water"
    with pytest.raises(rules.RuleError):
        rules.found_city(state, unit.id)


def test_buy_unit_cost() -> None:
    state = setup_state()
    unit = next(iter(state.units.values()))
    cid = rules.found_city(state, unit.id)
    state.players[0].prod = config.UNIT_STATS["scout"]["cost"]
    rules.buy_unit(state, cid, "scout")
    assert state.players[0].prod == 0


def test_win_condition() -> None:
    state = setup_state()
    unit = next(iter(state.units.values()))
    rules.found_city(state, unit.id)
    assert rules.check_win(state) is not None
