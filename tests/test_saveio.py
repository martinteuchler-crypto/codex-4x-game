import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from game.core import mapgen, saveio


def test_save_and_load_roundtrip(tmp_path):
    state = mapgen.generate_state(seed=4)
    data = saveio.dumps(state)
    loaded = saveio.loads(data)
    assert loaded.to_dict()["players"] == state.to_dict()["players"]
