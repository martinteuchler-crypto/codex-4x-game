import tempfile

from game.core import mapgen, saveio
from game.core.models import City, Player, State


def make_state() -> State:
    tiles, spawns = mapgen.generate_map(5, 5, seed=3)
    units = {u.id: u for u in mapgen.initial_units(spawns)}
    players = {0: Player(0), 1: Player(1)}
    tiles[0].improvements.update({"farm", "road"})
    city = City(
        id=1,
        owner=0,
        pos=(2, 2),
        size=1,
        claimed={(2, 2), (2, 3)},
        focus="prod",
        last_grow_turn=3,
    )
    state = State(5, 5, tiles, units, {city.id: city}, players)
    state.next_unit_id = max(units) + 1
    state.next_city_id = 2
    return state


def test_round_trip():
    state = make_state()
    with tempfile.TemporaryDirectory() as td:
        path = f"{td}/save.json"
        saveio.save_game(state, path)
        loaded = saveio.load_game(path)
    assert saveio.state_to_dict(state) == saveio.state_to_dict(loaded)
