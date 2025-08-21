from __future__ import annotations

from random import Random
from typing import Dict, List, Tuple

from ..config import UNIT_STATS
from .models import Tile, Unit


def generate_map(
    w: int, h: int, seed: int
) -> Tuple[Dict[Tuple[int, int], Tile], List[Tuple[int, int]]]:
    rng = Random(seed)
    tiles: Dict[Tuple[int, int], Tile] = {}
    for y in range(h):
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                kind = "water"
            else:
                kind = rng.choices(["plains", "forest", "hill", "water"], [6, 2, 2, 1])[
                    0
                ]
            tiles[(x, y)] = Tile(x, y, kind)
    spawns = [(1, 1), (w - 2, h - 2)]
    for s in spawns:
        tiles[s].kind = "plains"
    return tiles, spawns


def initial_units(spawns: List[Tuple[int, int]]) -> List[Unit]:
    units: List[Unit] = []
    for owner, pos in enumerate(spawns):
        u = Unit(
            id=-1,
            owner=owner,
            kind="scout",
            pos=pos,
            moves_left=UNIT_STATS["scout"]["moves"],
        )
        units.append(u)
    return units


__all__ = ["generate_map", "initial_units"]
