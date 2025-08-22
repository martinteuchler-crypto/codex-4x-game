"""Rendering utilities."""

from __future__ import annotations

import pygame

from .. import config
from ..core.models import State

COLORS = {
    "plains": (200, 200, 150),
    "forest": (34, 139, 34),
    "hill": (139, 137, 137),
    "water": (65, 105, 225),
    "fog": (0, 0, 0),
    "city": (255, 215, 0),
    "scout": (255, 255, 255),
    "soldier": (255, 0, 0),
}


def draw(state: State, surface: pygame.Surface) -> None:
    ts = config.TILE_SIZE
    for tile in state.tiles:
        rect = pygame.Rect(tile.x * ts, tile.y * ts, ts, ts)
        color = COLORS[tile.kind]
        surface.fill(color, rect)
        if state.current_player not in tile.revealed_by:
            surface.fill(COLORS["fog"], rect)
    for city in state.cities.values():
        rect = pygame.Rect(city.pos[0] * ts, city.pos[1] * ts, ts, ts)
        surface.fill(COLORS["city"], rect)
    for unit in state.units.values():
        rect = pygame.Rect(unit.pos[0] * ts + 8, unit.pos[1] * ts + 8, ts - 16, ts - 16)
        surface.fill(COLORS[unit.kind], rect)
