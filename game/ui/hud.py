"""HUD with pygame_gui buttons."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.models import State


class HUD:
    def __init__(self, rect: pygame.Rect) -> None:
        self.manager = pygame_gui.UIManager(rect.size)
        self.end_turn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 5, 80, 30),
            text="End Turn",
            manager=self.manager,
        )
        self.found_city = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 5, 100, 30),
            text="Found City",
            manager=self.manager,
        )
        self.buy_scout = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(210, 5, 100, 30),
            text="Buy Scout",
            manager=self.manager,
        )
        self.buy_soldier = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(320, 5, 100, 30),
            text="Buy Soldier",
            manager=self.manager,
        )
        self.info = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(430, 5, 200, 30),
            text="",
            manager=self.manager,
        )
        self.hint = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 40, 300, 20),
            text="",
            manager=self.manager,
        )
        self.hint.hide()
        self.message = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(320, 40, 300, 20),
            text="",
            manager=self.manager,
        )
        self.message.hide()

    def process_event(self, event: pygame.event.Event) -> None:
        self.manager.process_events(event)

    def update(self, time_delta: float, state: State) -> None:
        player = state.players[state.current_player]
        self.info.set_text(
            f"Turn {state.turn} Player {state.current_player} "
            f"F:{player.food} P:{player.prod}"
        )
        self.manager.update(time_delta)

    def draw(self, surface: pygame.Surface) -> None:
        self.manager.draw_ui(surface)

    def show_hint(self, text: str) -> None:
        self.hint.set_text(text)
        self.hint.show()

    def hide_hint(self) -> None:
        self.hint.hide()

    def show_message(self, text: str) -> None:
        """Display a transient warning or info message."""
        self.message.set_text(text)
        self.message.show()

    def hide_message(self) -> None:
        self.message.hide()
