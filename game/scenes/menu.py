"""Menu scene."""

from __future__ import annotations

import pygame
import pygame_gui

from .. import config
from .gameplay import Gameplay


class Menu:
    def __init__(self) -> None:
        self.manager = pygame_gui.UIManager((640, 480))
        self.new = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(270, 150, 100, 50),
            text="New Game",
            manager=self.manager,
        )
        self.quit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(270, 220, 100, 50),
            text="Quit",
            manager=self.manager,
        )

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (
                    event.type == pygame.USEREVENT
                    and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                ):
                    if event.ui_element == self.new:
                        game = Gameplay(config.START_SIZE, seed=1)
                        game.run()
                    elif event.ui_element == self.quit:
                        running = False
                self.manager.process_events(event)
            self.manager.update(time_delta)
            surface = pygame.display.get_surface()
            surface.fill((0, 0, 0))
            self.manager.draw_ui(surface)
            pygame.display.flip()
