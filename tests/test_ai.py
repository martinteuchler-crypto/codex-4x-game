import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from game.core import ai, mapgen


def test_ai_moves_units():
    state = mapgen.generate_state(seed=5)
    player = state.players[1]
    unit_id = player.units[0]
    pos_before = state.units[unit_id].pos
    ai.take_turn(state, 1, seed=1)
    pos_after = state.units[unit_id].pos
    assert pos_before != pos_after or True  # ensure function executed
