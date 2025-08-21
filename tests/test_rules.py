import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from game.core import mapgen, rules
from game.config import MOVE_COST, UNIT_STATS


def test_move_cost_respected():
    state = mapgen.generate_state(seed=2)
    unit_id = state.players[0].units[0]
    unit = state.units[unit_id]
    dest = (min(state.width - 1, unit.pos[0] + 1), unit.pos[1])
    cost = MOVE_COST[rules.get_tile(state, dest).kind]
    unit.moves_left = cost
    moved = rules.move_unit(state, unit_id, dest)
    assert moved
    assert unit.pos == dest


def test_end_turn_refreshes_moves():
    state = mapgen.generate_state(seed=3)
    unit_id = state.players[0].units[0]
    unit = state.units[unit_id]
    unit.moves_left = 0
    rules.end_turn(state)
    assert unit.moves_left == UNIT_STATS[unit.kind]["moves"]
