"""Data models for the 4X game."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple

Coord = Tuple[int, int]


@dataclass
class Tile:
    x: int
    y: int
    kind: str
    habitable: bool = False
    revealed_by: Set[int] = field(default_factory=set)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["revealed_by"] = list(self.revealed_by)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Tile":
        t = Tile(d["x"], d["y"], d["kind"], d.get("habitable", False))
        t.revealed_by = set(d.get("revealed_by", []))
        return t


@dataclass
class Unit:
    id: int
    owner: int
    kind: str
    pos: Coord
    moves_left: int

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Unit":
        return Unit(**d)


@dataclass
class City:
    id: int
    owner: int
    pos: Coord
    role: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "City":
        return City(**d)


@dataclass
class Player:
    id: int
    credits: int = 0
    metal: int = 0
    research: int = 0
    tech_unlocked: Set[str] = field(default_factory=set)
    tech_progress: Dict[str, int] = field(default_factory=dict)
    active_tech: Optional[str] = None
    units: List[int] = field(default_factory=list)
    cities: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tech_unlocked"] = list(self.tech_unlocked)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Player":
        d = dict(d)
        d["tech_unlocked"] = set(d.get("tech_unlocked", []))
        return Player(**d)


@dataclass
class State:
    width: int
    height: int
    tiles: List[Tile]
    units: Dict[int, Unit]
    cities: Dict[int, City]
    players: Dict[int, Player]
    current_player: int
    turn: int
    next_unit_id: int = 1
    next_city_id: int = 1
    seed: int = 0

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "tiles": [t.to_dict() for t in self.tiles],
            "units": {uid: u.to_dict() for uid, u in self.units.items()},
            "cities": {cid: c.to_dict() for cid, c in self.cities.items()},
            "players": {pid: p.to_dict() for pid, p in self.players.items()},
            "current_player": self.current_player,
            "turn": self.turn,
            "next_unit_id": self.next_unit_id,
            "next_city_id": self.next_city_id,
            "seed": self.seed,
        }

    @staticmethod
    def from_dict(d: dict) -> "State":
        return State(
            width=d["width"],
            height=d["height"],
            tiles=[Tile.from_dict(td) for td in d["tiles"]],
            units={int(k): Unit.from_dict(v) for k, v in d["units"].items()},
            cities={int(k): City.from_dict(v) for k, v in d["cities"].items()},
            players={int(k): Player.from_dict(v) for k, v in d["players"].items()},
            current_player=d["current_player"],
            turn=d["turn"],
            next_unit_id=d.get("next_unit_id", 1),
            next_city_id=d.get("next_city_id", 1),
            seed=d.get("seed", 0),
        )
