from tempfile import TemporaryDirectory

from game import config
from game.core import rules, saveio


def test_roundtrip() -> None:
    state = rules.new_game(5, 5, seed=2)
    unit = next(iter(state.units.values()))
    cid = rules.found_city(state, unit.id)
    state.players[0].prod = config.UNIT_STATS["scout"]["cost"]
    rules.buy_unit(state, cid, "scout")
    with TemporaryDirectory() as d:
        path = f"{d}/save.json"
        saveio.save_game(state, path)
        loaded = saveio.load_game(path)
    assert loaded.width == state.width
    assert len(loaded.units) == len(state.units)
    assert len(loaded.cities) == len(state.cities)
