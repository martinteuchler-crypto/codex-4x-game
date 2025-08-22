"""HUD with pygame_gui buttons."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.models import State


class HUD:
    def __init__(self, rect: pygame.Rect) -> None:
        self.manager = pygame_gui.UIManager(rect.size)
        self.end_turn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 10, 80, 40),
            text="End Turn",
            manager=self.manager,
        )
        self.found_city = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 10, 100, 40),
            text="Found City",
            manager=self.manager,
        )
        self.buy_scout = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(210, 10, 100, 40),
            text="Buy Scout",
            manager=self.manager,
        )
        self.buy_soldier = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(320, 10, 100, 40),
            text="Buy Soldier",
            manager=self.manager,
        )
        remaining = rect.width - 430
        info_width = max((remaining // 2) - 5, 50)
        hover_x = 430 + info_width + 10
        hover_width = rect.width - hover_x - 10
        self.info = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(430, 10, info_width, 40),
            text="",
            manager=self.manager,
        )
        self.hover_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(hover_x, 10, hover_width, 40),
            text="",
            manager=self.manager,
        )
        self.hover_text: str = ""

    def process_event(self, event: pygame.event.Event) -> None:
        self.manager.process_events(event)

    def update(self, time_delta: float, state: State) -> None:
        self.info.set_text(
            f"Turn {state.turn} Player {state.current_player} "
            f"F:{state.players[0].food} P:{state.players[0].prod}"
        )
        self.hover_label.set_text(self.hover_text)
        self.manager.update(time_delta)

    def set_hover(self, text: str) -> None:
        self.hover_text = text
        self.hover_label.set_text(text)

    def draw(self, surface: pygame.Surface) -> None:
        self.manager.draw_ui(surface)
