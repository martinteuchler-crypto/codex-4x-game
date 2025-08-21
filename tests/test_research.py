import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from game.core import tech, mapgen


def test_research_unlocks():
    state = mapgen.generate_state(seed=1)
    player = state.players[0]
    player.active_tech = "T1_PROPULSION"
    for _ in range(25):
        tech.apply_research_income(state, 0)
    assert "T1_PROPULSION" in player.tech_unlocked
