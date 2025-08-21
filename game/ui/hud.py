from __future__ import annotations

import pygame
from pygame import Surface

from ..core.models import Player


class ResourceHUD:
    """HUD element that displays current resources and next turn gain."""

    def __init__(self, player: Player, font: pygame.font.Font | None = None) -> None:
        self.player = player
        self.font = font or pygame.font.SysFont(None, 24)
        self.color = pygame.Color("white")

    def render(self, surface: Surface) -> None:
        food_gain, prod_gain = self.player.resource_gain()
        lines = [
            f"Food: {self.player.food} (+{food_gain})",
            f"Production: {self.player.production} (+{prod_gain})",
        ]
        for i, text in enumerate(lines):
            img = self.font.render(text, True, self.color)
            surface.blit(img, (10, 10 + i * 20))


__all__ = ["ResourceHUD"]
