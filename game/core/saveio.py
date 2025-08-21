"""Save and load game state to JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .models import State


def save_state(state: State, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f)


def load_state(path: str | Path) -> State:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return State.from_dict(data)


def dumps(state: State) -> str:
    return json.dumps(state.to_dict())


def loads(data: str) -> State:
    return State.from_dict(json.loads(data))
