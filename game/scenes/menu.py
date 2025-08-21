from __future__ import annotations

import pygame
import pygame_gui

from .. import config
from .gameplay import Gameplay


class Menu:
    def __init__(self) -> None:
        self.size = config.START_SIZE
        self.seed = 0
        w, h = self.size
        screen_size = (w * config.TILE_SIZE, h * config.TILE_SIZE + config.UI_BAR_H)
        self.manager = pygame_gui.UIManager(screen_size)
        y = h * config.TILE_SIZE
        self.new_btn = pygame_gui.elements.UIButton(
            pygame.Rect(0, y, 100, config.UI_BAR_H), "New Game", self.manager
        )
        self.quit_btn = pygame_gui.elements.UIButton(
            pygame.Rect(110, y, 100, config.UI_BAR_H), "Quit", self.manager
        )
        self.screen_size = screen_size

    def run(self) -> None:
        screen = pygame.display.set_mode(self.screen_size)
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.manager.process_events(event)
                if (
                    event.type == pygame.USEREVENT
                    and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                ):
                    if event.ui_element == self.new_btn:
                        Gameplay(self.size, self.seed).run()
                    elif event.ui_element == self.quit_btn:
                        running = False
            self.manager.update(time_delta)
            screen.fill((0, 0, 0))
            self.manager.draw_ui(screen)
            pygame.display.flip()


__all__ = ["Menu"]
