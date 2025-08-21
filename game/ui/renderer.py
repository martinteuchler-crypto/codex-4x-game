from __future__ import annotations

import pygame

from .. import config
from ..core.models import State

COLORS = {
    "plains": (80, 200, 120),
    "forest": (16, 160, 0),
    "hill": (160, 120, 80),
    "water": (30, 30, 200),
    "fog": (0, 0, 0),
}
UNIT_COLORS = {0: (0, 0, 0), 1: (200, 0, 0)}


def draw(state: State, surface: pygame.Surface, owner: int) -> None:
    for tile in state.tiles.values():
        rect = pygame.Rect(
            tile.x * config.TILE_SIZE,
            tile.y * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE,
        )
        if owner in tile.revealed_by:
            color = COLORS[tile.kind]
        else:
            color = COLORS["fog"]
        pygame.draw.rect(surface, color, rect)
    for city in state.cities.values():
        rect = pygame.Rect(
            city.pos[0] * config.TILE_SIZE + 8,
            city.pos[1] * config.TILE_SIZE + 8,
            16,
            16,
        )
        pygame.draw.rect(surface, UNIT_COLORS[city.owner], rect)
    for unit in state.units.values():
        rect = pygame.Rect(
            unit.pos[0] * config.TILE_SIZE + 4,
            unit.pos[1] * config.TILE_SIZE + 4,
            24,
            24,
        )
        pygame.draw.rect(surface, UNIT_COLORS[unit.owner], rect)


__all__ = ["draw"]
