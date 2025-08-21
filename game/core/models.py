from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

Coord = Tuple[int, int]


@dataclass
class City:
    """A simple city that yields fixed resources each turn."""

    pos: Coord
    food_yield: int
    prod_yield: int


@dataclass
class Player:
    """Represents a player and their global resources."""

    food: int = 0
    production: int = 0
    cities: List[City] = field(default_factory=list)

    def resource_gain(self) -> Tuple[int, int]:
        """Return the total (food, production) gain for the next turn."""
        food_gain = sum(city.food_yield for city in self.cities)
        prod_gain = sum(city.prod_yield for city in self.cities)
        return food_gain, prod_gain

    def apply_gain(self) -> None:
        """Apply the resource gain to this player."""
        food_gain, prod_gain = self.resource_gain()
        self.food += food_gain
        self.production += prod_gain


__all__ = ["City", "Player", "Coord"]
