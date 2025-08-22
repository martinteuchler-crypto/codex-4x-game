"""Data models for the 4X game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Coord = Tuple[int, int]


@dataclass
class Tile:
    x: int
    y: int
    kind: str  # 'plains' | 'forest' | 'hill' | 'water'
    revealed_by: Set[int] = field(default_factory=set)


@dataclass
class Unit:
    id: int
    owner: int  # 0 human, 1 ai
    kind: str  # 'scout' | 'soldier' | 'settler'
    pos: Coord
    moves_left: int


@dataclass
class City:
    id: int
    owner: int
    pos: Coord
    size: int = 1
    claimed: Set[Coord] = field(default_factory=set)
      
    def claim(self, coord: Coord) -> None:
        """Add a coordinate to the city's claimed tiles."""
        self.claimed.add(coord)

@dataclass
class Player:
    id: int
    food: int = 0
    prod: int = 0


@dataclass
class State:
    width: int
    height: int
    tiles: List[Tile]
    units: Dict[int, Unit]
    cities: Dict[int, City]
    players: Dict[int, Player]
    current_player: int = 0
    turn: int = 1
    next_unit_id: int = 1
    next_city_id: int = 1

    def tile_at(self, coord: Coord) -> Tile:
        x, y = coord
        return self.tiles[y * self.width + x]

    def units_at(self, coord: Coord) -> List[Unit]:
        return [u for u in self.units.values() if u.pos == coord]

    def city_at(self, coord: Coord) -> Optional[City]:
        for city in self.cities.values():
            if city.pos == coord:
                return city
        return None


__all__ = [
    "City",
    "Coord",
    "Player",
    "State",
    "Tile",
    "Unit",
]
