"""Rendering helpers using pygame."""

from __future__ import annotations

import pygame

from ..config import TILE_SIZE, UI_BAR_H
from ..core.models import State

COLORS = {
    "deep_space": (0, 0, 20),
    "asteroids": (80, 80, 80),
    "nebula": (40, 0, 80),
    "star": (200, 200, 0),
}
UNIT_COLOR = {0: (0, 255, 0), 1: (255, 0, 0)}


def render(state: State, screen: pygame.Surface) -> None:
    for tile in state.tiles:
        rect = pygame.Rect(
            tile.x * TILE_SIZE, tile.y * TILE_SIZE + UI_BAR_H, TILE_SIZE, TILE_SIZE
        )
        pygame.draw.rect(screen, COLORS[tile.kind], rect)
    for unit in state.units.values():
        cx = unit.pos[0] * TILE_SIZE + TILE_SIZE // 2
        cy = unit.pos[1] * TILE_SIZE + UI_BAR_H + TILE_SIZE // 2
        pygame.draw.circle(screen, UNIT_COLOR[unit.owner], (cx, cy), TILE_SIZE // 3)
