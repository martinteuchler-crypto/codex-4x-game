import tempfile
from game.core import mapgen, saveio
from game.core.models import Player, State


def make_state() -> State:
    tiles, spawns = mapgen.generate_map(5, 5, seed=3)
    units = {u.id: u for u in mapgen.initial_units(spawns)}
    players = {0: Player(0), 1: Player(1)}
    state = State(5, 5, tiles, units, {}, players)
    return state


def test_round_trip():
    state = make_state()
    with tempfile.TemporaryDirectory() as td:
        path = f"{td}/save.json"
        saveio.save_game(state, path)
        loaded = saveio.load_game(path)
    assert saveio.state_to_dict(state) == saveio.state_to_dict(loaded)
