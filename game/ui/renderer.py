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
CLAIM_COLOR = (255, 255, 0)
SELECT_COLOR = (255, 0, 255)
INFRA_COLORS = {
    "farm": (144, 238, 144),
    "mine": (169, 169, 169),
    "saw": (160, 82, 45),
    "road": (105, 105, 105),
}
FONT: pygame.font.Font | None = None
FONT_SIZE = 0


def draw(
    state: State,
    surface: pygame.Surface,
    selected_unit_id: int | None = None,
    selected_city_id: int | None = None,
    selected_tile: tuple[int, int] | None = None,
) -> None:
    global FONT, FONT_SIZE
    ts = config.TILE_SIZE
    font_px = max(12, ts // 2)
    if FONT is None or FONT_SIZE != font_px:
        FONT = pygame.font.Font(None, font_px)
        FONT_SIZE = font_px
    move_points: dict[tuple[int, int], tuple[int, int]] = {}
    for tile in state.tiles:
        rect = pygame.Rect(tile.x * ts, tile.y * ts, ts, ts)
        color = COLORS[tile.kind]
        surface.fill(color, rect)
        if state.current_player in tile.revealed_by:
            if "road" in tile.improvements:
                pygame.draw.line(
                    surface, INFRA_COLORS["road"], rect.midleft, rect.midright, 2
                )
                pygame.draw.line(
                    surface, INFRA_COLORS["road"], rect.midtop, rect.midbottom, 2
                )
            for imp in tile.improvements:
                if imp == "road":
                    continue
                inner = pygame.Rect(
                    rect.x + ts // 4, rect.y + ts // 4, ts // 2, ts // 2
                )
                surface.fill(INFRA_COLORS[imp], inner)
        else:
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
        if unit.moves_left > 0:
            max_moves = config.UNIT_STATS[unit.kind]["moves"]
            prev = move_points.get(unit.pos, (0, max_moves))
            move_points[unit.pos] = (max(unit.moves_left, prev[0]), max_moves)
        if unit.kind == "soldier":
            soldier_counts[unit.pos] = soldier_counts.get(unit.pos, 0) + 1
    for coord, count in soldier_counts.items():
        rect = pygame.Rect(coord[0] * ts, coord[1] * ts, ts, ts)
        if FONT:
            text = FONT.render(f"#{count}", True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
    for coord, (moves, max_moves) in move_points.items():
        seg_w = max(1, ts // max_moves)
        for i in range(moves):
            seg_rect = pygame.Rect(
                coord[0] * ts + i * seg_w,
                coord[1] * ts,
                seg_w - 1,
                4,
            )
            pygame.draw.rect(surface, (0, 255, 0), seg_rect)
    for city in state.cities.values():
        claimed = getattr(city, "claimed", {city.pos})
        for coord in claimed:
            tile = state.tile_at(coord)
            if state.current_player in tile.revealed_by:
                rect = pygame.Rect(coord[0] * ts, coord[1] * ts, ts, ts)
                pygame.draw.rect(surface, CLAIM_COLOR, rect, 2)
    if selected_tile is not None:
        rect = pygame.Rect(selected_tile[0] * ts, selected_tile[1] * ts, ts, ts)
        pygame.draw.rect(surface, SELECT_COLOR, rect, 3)
    if selected_unit_id is not None and selected_unit_id in state.units:
        unit = state.units[selected_unit_id]
        rect = pygame.Rect(unit.pos[0] * ts, unit.pos[1] * ts, ts, ts)
        pygame.draw.rect(surface, SELECT_COLOR, rect, 3)
    if selected_city_id is not None and selected_city_id in state.cities:
        city = state.cities[selected_city_id]
        rect = pygame.Rect(city.pos[0] * ts, city.pos[1] * ts, ts, ts)
        pygame.draw.rect(surface, SELECT_COLOR, rect, 3)
