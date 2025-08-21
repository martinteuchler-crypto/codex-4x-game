from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

Coord = Tuple[int, int]


@dataclass
class Tile:
    x: int
    y: int
    kind: str
    revealed_by: set[int] = field(default_factory=set)


@dataclass
class Unit:
    id: int
    owner: int
    kind: str
    pos: Coord
    moves_left: int


@dataclass
class City:
    id: int
    owner: int
    pos: Coord


@dataclass
class Player:
    id: int
    food: int = 0
    prod: int = 0


@dataclass
class State:
    width: int
    height: int
    tiles: Dict[Coord, Tile]
    units: Dict[int, Unit]
    cities: Dict[int, City]
    players: Dict[int, Player]
    current: int = 0
    turn: int = 1
    next_id: int = 0

    def gen_id(self) -> int:
        self.next_id += 1
        return self.next_id


__all__ = [
    "Coord",
    "Tile",
    "Unit",
    "City",
    "Player",
    "State",
]
