"""HUD with pygame_gui buttons."""

from __future__ import annotations

import pygame
import pygame_gui

from ..core.models import State


class HUD:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        # UIManager needs the full screen size so elements can be positioned
        # anywhere. A panel constrained to ``rect`` holds all HUD widgets so
        # that their coordinates are relative to the HUD area rather than the
        # map. This prevents map click handling from interfering with HUD
        # interactions.
        screen_size = pygame.display.get_surface().get_size()
        self.manager = pygame_gui.UIManager(screen_size)
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
        )
        self.end_turn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 5, 80, 30),
            text="End Turn",
            container=self.panel,
            manager=self.manager,
        )
        self.found_city = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 5, 100, 30),
            text="Found City",
            container=self.panel,
            manager=self.manager,
        )
        self.buy_unit = pygame_gui.elements.UIDropDownMenu(
            options_list=["Buy Unit", "Buy Scout", "Buy Soldier", "Buy Settler"],
            starting_option="Buy Unit",
            relative_rect=pygame.Rect(210, 5, 150, 30),
            container=self.panel,
            manager=self.manager,
        )
        self.buy_unit.disable()
        self.info = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(370, 5, 200, 30),
            text="",
            container=self.panel,
            manager=self.manager,
        )
        self.hover_info = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                self.rect.width - 210, self.rect.height - 30, 200, 20
            ),
            text="",
            container=self.panel,
            manager=self.manager,
        )
        self.hover_info.hide()
        self.message = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, self.rect.height - 30, 300, 20),
            text="",
            container=self.panel,
            manager=self.manager,
        )
        self.message.text_colour = pygame.Color("red")
        self.message.rebuild()
        self.message.hide()
        self._message_timer: float | None = None

    def process_event(self, event: pygame.event.Event) -> None:
        self.manager.process_events(event)

    def update(self, time_delta: float, state: State) -> None:
        player = state.players[state.current_player]
        self.info.set_text(
            f"Turn {state.turn} Player {state.current_player} "
            f"F:{player.food} P:{player.prod}"
        )
        if self._message_timer is not None:
            self._message_timer -= time_delta
            if self._message_timer <= 0:
                self.message.hide()
                self._message_timer = None
        self.manager.update(time_delta)

    def draw(self, surface: pygame.Surface) -> None:
        self.manager.draw_ui(surface)

    def set_hover_info(self, text: str) -> None:
        self.hover_info.set_text(text)
        self.hover_info.show()

    def clear_hover_info(self) -> None:
        self.hover_info.hide()

    def show_message(self, text: str, timeout: float | None = None) -> None:
        self.message.set_text(text)
        self.message.show()
        self._message_timer = timeout

    def hide_message(self) -> None:
        """Hide any active message immediately."""
        self.message.hide()
        self._message_timer = None
