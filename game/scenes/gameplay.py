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
        size = self.screen.get_size()
        tile = config.compute_tile_size(size, (state.width, state.height))
        config.set_tile_size(tile)
        size = (
            tile * state.width,
            tile * state.height + config.UI_BAR_H,
        )
        pygame.display.set_mode(size, pygame.RESIZABLE)
        self.screen = pygame.display.get_surface()
        hud_rect = pygame.Rect(0, size[1] - config.UI_BAR_H, size[0], config.UI_BAR_H)
        self.hud = HUD(hud_rect)
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
                elif event.type == pygame.VIDEORESIZE:
                    requested = config.clamp_window_size((event.w, event.h))
                    tile = config.compute_tile_size(
                        requested, (self.state.width, self.state.height)
                    )
                    config.set_tile_size(tile)
                    new_size = (
                        tile * self.state.width,
                        tile * self.state.height + config.UI_BAR_H,
                    )
                    pygame.display.set_mode(new_size, pygame.RESIZABLE)
                    self.screen = pygame.display.get_surface()
                    self.hud.resize(new_size)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    running = False
                else:
                    self.input.handle_event(event, self.state, rng)
            if self.state.current_player == 1:
                ai.ai_turn(self.state, rng)
            self.hud.update(time_delta, self.state)
            draw(
                self.state,
                self.screen,
                self.input.selected,
                self.input.selected_city,
            )
            self.hud.draw(self.screen)
            pygame.display.flip()
            if check_win(self.state) is not None:
                running = False
