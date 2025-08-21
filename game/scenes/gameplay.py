from __future__ import annotations

from random import Random

import pygame
import pygame_gui

from .. import config
from ..core import ai, rules
from ..ui import renderer
from ..ui.hud import Hud
from ..ui.input import InputHandler


class Gameplay:
    def __init__(self, size: tuple[int, int], seed: int):
        self.state = rules.new_game(*size, seed)
        self.rng = Random(seed)
        w, h = size
        self.screen_size = (
            w * config.TILE_SIZE,
            h * config.TILE_SIZE + config.UI_BAR_H,
        )
        # ensure a display surface exists before creating UI elements
        self.screen = pygame.display.set_mode(self.screen_size)
        self.manager = pygame_gui.UIManager(self.screen_size)
        self.hud = Hud(self.manager)
        self.input = InputHandler()

    def run(self) -> None:
        pygame.display.set_caption("4X Prototype")
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.manager.process_events(event)
                self.input.handle(event, self.state)
                if (
                    event.type == pygame.USEREVENT
                    and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                ):
                    if event.ui_element == self.hud.end_btn:
                        rules.end_turn(self.state, self.rng)
                        if self.state.current == 1:
                            ai.ai_take_turn(self.state, self.rng)
                            rules.end_turn(self.state, self.rng)
                    elif (
                        event.ui_element == self.hud.city_btn
                        and self.input.selected is not None
                    ):
                        try:
                            rules.found_city(self.state, self.input.selected)
                            self.input.selected = None
                        except rules.RuleError:
                            pass
                    elif event.ui_element == self.hud.scout_btn:
                        self._buy_unit("scout")
                    elif event.ui_element == self.hud.soldier_btn:
                        self._buy_unit("soldier")
            self.manager.update(time_delta)
            renderer.draw(self.state, self.screen, self.state.current)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

    def _buy_unit(self, kind: str) -> None:
        for city in self.state.cities.values():
            if city.owner == self.state.current:
                try:
                    rules.buy_unit(self.state, city.id, kind)
                except rules.RuleError:
                    pass
                break


__all__ = ["Gameplay"]
