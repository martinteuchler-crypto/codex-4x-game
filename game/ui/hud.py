"""Simple HUD rendering."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.models import State
from ..config import UI_BAR_H


def draw_hud(
    state: State, screen: pygame.Surface, manager: pygame_gui.UIManager
) -> None:
    rect = pygame.Rect(0, 0, screen.get_width(), UI_BAR_H)
    pygame.draw.rect(screen, (20, 20, 20), rect)
    font = pygame.font.SysFont(None, 24)
    player = state.players[state.current_player]
    text = (
        f"Turn {state.turn} | C:{player.credits} M:{player.metal} R:{player.research}"
    )
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))
