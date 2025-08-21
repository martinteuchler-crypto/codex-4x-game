"""Menu scene."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.mapgen import generate_state


def run_menu(screen: pygame.Surface, manager: pygame_gui.UIManager):
    clock = pygame.time.Clock()
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (screen.get_width() // 2 - 100, screen.get_height() // 2 - 25), (200, 50)
        ),
        text="New Game",
        manager=manager,
    )
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            manager.process_events(event)
            if (
                event.type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == button
            ):
                return generate_state()
        manager.update(dt)
        screen.fill((0, 0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
