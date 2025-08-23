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
    "settler": (0, 255, 255),
}

HIGHLIGHT_COLOR = (255, 255, 0)
FONT: pygame.font.Font | None = None


def draw(
    state: State,
    surface: pygame.Surface,
    selected_unit_id: int | None = None,
    selected_city_id: int | None = None,
) -> None:
    global FONT
    if FONT is None:
        FONT = pygame.font.Font(None, 16)
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
        if FONT:
            text = FONT.render(str(city.size), True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
    soldier_counts: dict[tuple[int, int], int] = {}
    for unit in state.units.values():
        rect = pygame.Rect(unit.pos[0] * ts + 8, unit.pos[1] * ts + 8, ts - 16, ts - 16)
        surface.fill(COLORS[unit.kind], rect)
        if unit.kind == "soldier":
            soldier_counts[unit.pos] = soldier_counts.get(unit.pos, 0) + 1
    for coord, count in soldier_counts.items():
        rect = pygame.Rect(coord[0] * ts, coord[1] * ts, ts, ts)
        if FONT:
            text = FONT.render(f"#{count}", True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
    if selected_city_id is not None and selected_city_id in state.cities:
        city = state.cities[selected_city_id]
        claimed = getattr(city, "claimed", {city.pos})
        for coord in claimed:
            rect = pygame.Rect(coord[0] * ts, coord[1] * ts, ts, ts)
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect, 2)
    if selected_unit_id is not None and selected_unit_id in state.units:
        unit = state.units[selected_unit_id]
        tile = state.tile_at(unit.pos)
        if state.current_player in tile.revealed_by:
            rect = pygame.Rect(unit.pos[0] * ts, unit.pos[1] * ts, ts, ts)
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect, 2)
