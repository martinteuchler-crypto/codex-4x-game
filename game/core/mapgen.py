"""Procedural map generation."""

from __future__ import annotations

from random import Random
from typing import List, Tuple

from .. import config
from .models import Tile, Unit


def generate_map(w: int, h: int, seed: int) -> Tuple[List[Tile], List[Tuple[int, int]]]:
    rng = Random()
    tiles: List[Tile] = []
    for y in range(h):
        for x in range(w):
            if rng.random() < 0.1:
                kind = "water"
            elif rng.random() < 0.2:
                kind = "forest"
            elif rng.random() < 0.3:
                kind = "hill"
            else:
                kind = "plains"
            tiles.append(Tile(x=x, y=y, kind=kind))
    # spawn points at opposite corners on land
    spawns = [(1, 1), (w - 2, h - 2)]
    for sx, sy in spawns:
        idx = sy * w + sx
        tiles[idx].kind = "plains"
    return tiles, spawns


def initial_units(spawns: List[Tuple[int, int]]) -> List[Unit]:
    units: List[Unit] = []
    for i, pos in enumerate(spawns):
        units.append(
            Unit(
                id=i + 1,
                owner=i,
                kind="settler",
                pos=pos,
                moves_left=config.UNIT_STATS["settler"]["moves"],
            )
        )
    return units


__all__ = ["generate_map", "initial_units"]
