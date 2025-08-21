from __future__ import annotations

import pygame
import pygame_gui

from .. import config


class Hud:
    def __init__(self, manager: pygame_gui.UIManager):
        y = config.START_SIZE[1] * config.TILE_SIZE
        self.end_btn = pygame_gui.elements.UIButton(
            pygame.Rect(0, y, 100, config.UI_BAR_H), "End Turn", manager
        )
        self.city_btn = pygame_gui.elements.UIButton(
            pygame.Rect(110, y, 120, config.UI_BAR_H), "Found City", manager
        )
        self.scout_btn = pygame_gui.elements.UIButton(
            pygame.Rect(240, y, 120, config.UI_BAR_H), "Buy Scout", manager
        )
        self.soldier_btn = pygame_gui.elements.UIButton(
            pygame.Rect(370, y, 120, config.UI_BAR_H), "Buy Soldier", manager
        )


__all__ = ["Hud"]
