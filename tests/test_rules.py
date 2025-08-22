from random import Random

from game import config
from game.core import mapgen, rules
from game.core.models import Player, State


def make_state() -> State:
    tiles, spawns = mapgen.generate_map(5, 5, seed=1)
    units = {u.id: u for u in mapgen.initial_units(spawns)}
    players = {0: Player(0), 1: Player(1)}
    state = State(5, 5, tiles, units, {}, players)
    state.next_unit_id = max(units) + 1
    return state


def test_movement_cost_and_fog():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    dest = (state.units[uid].pos[0] + 1, state.units[uid].pos[1])
    rules.move_unit(state, uid, dest)
    assert state.units[uid].moves_left < config.UNIT_STATS["settler"]["moves"]
    tile = state.tile_at(dest)
    assert state.current_player in tile.revealed_by


def test_found_city_and_buy_unit():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    state.units[uid].pos = (2, 2)
    rng = Random(0)
    rules.found_city(state, uid, rng)
    cid = next(iter(state.cities))
    state.players[0].prod = 10
    rules.buy_unit(state, cid, "soldier")
    assert any(u.kind == "soldier" for u in state.units.values())


def test_buy_settler_costs_food_and_production():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    state.units[uid].pos = (2, 2)
    rng = Random(0)
    rules.found_city(state, uid, rng)
    cid = next(iter(state.cities))
    player = state.players[0]
    player.food = 2
    player.prod = 1
    rules.buy_unit(state, cid, "settler")
    assert any(u.kind == "settler" for u in state.units.values())
    assert player.food == 0 and player.prod == 0


def test_win_condition():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    state.units[uid].pos = (2, 2)
    state.tile_at((2, 2)).kind = "plains"
    rng = Random(0)
    rules.found_city(state, uid, rng)
    cid = next(iter(state.cities))
    state.cities[cid].owner = 1
    assert rules.check_win(state) == 1


def test_no_win_without_cities():
    state = make_state()
    assert rules.check_win(state) is None


def test_no_win_if_opponent_has_settler():
    state = make_state()
    uid = next(
        uid for uid, u in state.units.items() if u.kind == "settler" and u.owner == 0
    )
    state.units[uid].pos = (2, 2)
    state.tile_at((2, 2)).kind = "plains"
    rng = Random(0)
    rules.found_city(state, uid, rng)
    assert rules.check_win(state) is None


def test_end_turn_without_city():
    state = make_state()
    rules.end_turn(state)
    assert state.current_player == 1


def test_grow_city_cost_and_claim():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    state.units[uid].pos = (2, 2)
    city = rules.found_city(state, uid)
    player = state.players[city.owner]
    player.food = 10
    rng = Random(0)
    assert rules.grow_city(state, city, rng)
    assert city.size == 2
    assert len(city.claimed) == 2
    assert player.food == 8


def test_end_turn_uses_claimed_tiles_and_growth():
    state = make_state()
    uid = next(uid for uid, u in state.units.items() if u.kind == "settler")
    state.units[uid].pos = (2, 2)
    city = rules.found_city(state, uid)
    player = state.players[city.owner]
    city.claimed.add((2, 3))
    state.tile_at((2, 2)).kind = "plains"
    state.tile_at((2, 3)).kind = "forest"
    player.food = 2
    rules.end_turn(state)
    assert player.food == 1  # 2 + 1 (plains) + 0 (forest) - 2 (growth)
    assert player.prod == 3  # 1 (plains) + 2 (forest)
    assert city.size == 2
    assert len(city.claimed) == 3
