"""JSON save/load for game state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import City, Player, State, Tile, Unit


def state_to_dict(state: State) -> Dict[str, Any]:
    return {
        "width": state.width,
        "height": state.height,
        "tiles": [
            {
                "x": t.x,
                "y": t.y,
                "kind": t.kind,
                "revealed_by": list(t.revealed_by),
                "improvements": list(t.improvements),
            }
            for t in state.tiles
        ],
        "units": {
            uid: {
                "id": u.id,
                "owner": u.owner,
                "kind": u.kind,
                "pos": list(u.pos),
                "moves_left": u.moves_left,
            }
            for uid, u in state.units.items()
        },
        "cities": {
            cid: {
                "id": c.id,
                "owner": c.owner,
                "pos": list(c.pos),
                "size": c.size,
                "claimed": [list(s) for s in sorted(c.claimed)],
                "focus": c.focus,
                "last_grow_turn": c.last_grow_turn,
            }
            for cid, c in state.cities.items()
        },
        "players": {
            pid: {"id": p.id, "food": p.food, "prod": p.prod}
            for pid, p in state.players.items()
        },
        "current_player": state.current_player,
        "turn": state.turn,
        "next_unit_id": state.next_unit_id,
        "next_city_id": state.next_city_id,
    }


def dict_to_state(data: Dict[str, Any]) -> State:
    tiles = [
        Tile(
            x=t["x"],
            y=t["y"],
            kind=t["kind"],
            revealed_by=set(t["revealed_by"]),
            improvements=set(t.get("improvements", [])),
        )
        for t in data["tiles"]
    ]
    units = {
        int(uid): Unit(
            id=u["id"],
            owner=u["owner"],
            kind=u["kind"],
            pos=tuple(u["pos"]),
            moves_left=u["moves_left"],
        )
        for uid, u in data["units"].items()
    }
    cities = {
        int(cid): City(
            id=c["id"],
            owner=c["owner"],
            pos=tuple(c["pos"]),
            size=c.get("size", 1),
            claimed={tuple(s) for s in c.get("claimed", [])},
            focus=c.get("focus", "food"),
            last_grow_turn=c.get("last_grow_turn", -1),
        )
        for cid, c in data["cities"].items()
    }
    players = {int(pid): Player(**p) for pid, p in data["players"].items()}
    return State(
        width=data["width"],
        height=data["height"],
        tiles=tiles,
        units=units,
        cities=cities,
        players=players,
        current_player=data["current_player"],
        turn=data["turn"],
        next_unit_id=data["next_unit_id"],
        next_city_id=data["next_city_id"],
    )


def save_game(state: State, path: str | Path) -> None:
    Path(path).write_text(json.dumps(state_to_dict(state)))


def load_game(path: str | Path) -> State:
    data = json.loads(Path(path).read_text())
    return dict_to_state(data)


__all__ = ["save_game", "load_game", "state_to_dict", "dict_to_state"]
