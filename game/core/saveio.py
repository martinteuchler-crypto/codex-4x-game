from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import City, Player, State, Tile, Unit


def save_game(state: State, path: str | Path) -> None:
    data: Dict[str, Any] = {
        "size": [state.width, state.height],
        "current": state.current,
        "turn": state.turn,
        "next_id": state.next_id,
        "tiles": [
            {"x": t.x, "y": t.y, "kind": t.kind, "revealed": list(t.revealed_by)}
            for t in state.tiles.values()
        ],
        "units": [
            {
                "id": u.id,
                "owner": u.owner,
                "kind": u.kind,
                "pos": list(u.pos),
                "moves_left": u.moves_left,
            }
            for u in state.units.values()
        ],
        "cities": [
            {"id": c.id, "owner": c.owner, "pos": list(c.pos)}
            for c in state.cities.values()
        ],
        "players": [
            {"id": p.id, "food": p.food, "prod": p.prod} for p in state.players.values()
        ],
    }
    Path(path).write_text(json.dumps(data))


def load_game(path: str | Path) -> State:
    data = json.loads(Path(path).read_text())
    w, h = data["size"]
    tiles = {
        (t["x"], t["y"]): Tile(t["x"], t["y"], t["kind"], set(t["revealed"]))
        for t in data["tiles"]
    }
    players = {p["id"]: Player(p["id"], p["food"], p["prod"]) for p in data["players"]}
    units = {
        u["id"]: Unit(u["id"], u["owner"], u["kind"], tuple(u["pos"]), u["moves_left"])
        for u in data["units"]
    }
    cities = {
        c["id"]: City(c["id"], c["owner"], tuple(c["pos"])) for c in data["cities"]
    }
    state = State(
        w,
        h,
        tiles,
        units,
        cities,
        players,
        data["current"],
        data["turn"],
        data["next_id"],
    )
    return state


__all__ = ["save_game", "load_game"]
