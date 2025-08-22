"""Gameplay scene."""

from __future__ import annotations

from random import Random

import pygame

from .. import config
from ..core import ai
from ..core.models import State
from ..core.rules import check_win
from ..ui.hud import HUD
from ..ui.input import InputHandler
from ..ui.renderer import draw


class Gameplay:
    def __init__(self, state: State) -> None:
        self.state = state
        self.screen = pygame.display.get_surface()
        self.hud = HUD(
            pygame.Rect(
                0,
                state.height * config.TILE_SIZE,
                state.width * config.TILE_SIZE,
                config.UI_BAR_H,
            )
        )
        self.input = InputHandler(self.hud)

    def run(self) -> None:
        clock = pygame.time.Clock()
        rng = Random()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    running = False
                else:
                    self.input.handle_event(event, self.state, rng)
            if self.state.current_player == 1:
                ai.ai_turn(self.state, rng)
            self.hud.update(time_delta, self.state)
            draw(self.state, self.screen, self.input.selected)
            self.hud.draw(self.screen)
            pygame.display.flip()
            if check_win(self.state) is not None:
                running = False
