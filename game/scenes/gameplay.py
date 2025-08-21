"""Gameplay scene."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.ai import take_turn
from ..core.models import State
from ..ui import hud, input as input_mod, renderer


def run_game(
    screen: pygame.Surface, manager: pygame_gui.UIManager, state: State
) -> None:
    clock = pygame.time.Clock()
    selected: int | None = None
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            manager.process_events(event)
            selected = input_mod.handle_event(state, event, selected)
        if state.current_player == 1:
            take_turn(state, 1)
            state.current_player = 0
        manager.update(dt)
        screen.fill((0, 0, 0))
        renderer.render(state, screen)
        hud.draw_hud(state, screen, manager)
        manager.draw_ui(screen)
        pygame.display.flip()
