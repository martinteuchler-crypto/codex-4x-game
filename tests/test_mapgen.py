from game import config
from game.core import mapgen


def test_initial_unit_moves_left():
    tiles, spawns = mapgen.generate_map(5, 5, seed=0)
    units = mapgen.initial_units(spawns)
    settler = next(u for u in units if u.kind == "settler")
    scout = next(u for u in units if u.kind == "scout")
    assert settler.moves_left == config.UNIT_STATS["settler"]["moves"]
    assert scout.moves_left == config.UNIT_STATS["scout"]["moves"]
    assert settler.moves_left != scout.moves_left
