"""HUD with pygame_gui buttons."""

from __future__ import annotations

import pygame
import pygame_gui

from .. import config
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
        # Create the buy-unit menu without the HUD panel as its container so it
        # can expand over the map area when opened.
        self.buy_unit = pygame_gui.elements.UIDropDownMenu(
            options_list=["Buy Unit", "Buy Scout", "Buy Soldier", "Buy Settler"],
            starting_option="Buy Unit",
            relative_rect=pygame.Rect(self.rect.x + 210, self.rect.y + 5, 150, 30),
            manager=self.manager,
            anchors={"left": "left", "top": "top"},
        )
        # Expand upwards so the menu remains fully visible above the HUD
        self.buy_unit.expand_direction = "up"
        for state in self.buy_unit.menu_states.values():
            state.expand_direction = "up"
        self.buy_unit.rebuild()
        self.buy_unit.disable()
        self.focus = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(370, 5, 100, 30),
            text="Food",
            container=self.panel,
            manager=self.manager,
        )
        self.focus.disable()
        self.info = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(480, 5, 150, 30),
            text="",
            container=self.panel,
            manager=self.manager,
        )
        self.build_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 35, 220, 25),
            container=self.panel,
            manager=self.manager,
        )
        self.build_buttons = {
            name: pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(i * 55, 0, 55, 25),
                text=label,
                container=self.build_panel,
                manager=self.manager,
            )
            for i, (name, label) in enumerate(
                [("farm", "Farm"), ("mine", "Mine"), ("saw", "Saw"), ("road", "Road")]
            )
        }
        self.build_panel.hide()
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

    def resize(self, size: tuple[int, int]) -> None:
        """Resize HUD elements to match the new window ``size``."""
        self.rect.y = size[1] - self.rect.height
        self.rect.width = size[0]
        self.manager.set_window_resolution(size)
        self.panel.set_relative_position(self.rect.topleft)
        self.panel.set_dimensions((self.rect.width, self.rect.height))
        self.buy_unit.set_relative_position((210, self.rect.y + 5))
        self.focus.set_relative_position((370, 5))
        self.info.set_relative_position((480, 5))
        self.build_panel.set_relative_position((10, 35))
        self.hover_info.set_relative_position(
            (self.rect.width - 210, self.rect.height - 30)
        )

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

    def reset_buy_unit(self) -> None:
        """Return the buy-unit menu to its placeholder option."""
        self.buy_unit.selected_option = ("Buy Unit", "Buy Unit")
        if self.buy_unit.current_state is not None:
            self.buy_unit.current_state.selected_option = self.buy_unit.selected_option
            self.buy_unit.current_state.rebuild()

    def set_focus_option(self, option: str) -> None:
        """Set the focus button text to ``option``."""
        self.focus.set_text(option)

    def show_build_options(self, state: State, coord: tuple[int, int]) -> None:
        tile = state.tile_at(coord)
        player = state.players[state.current_player]
        for kind, button in self.build_buttons.items():
            info = config.INFRASTRUCTURE[kind]
            allowed = (
                tile.kind in info["required"]
                and (kind == "road" or not tile.improvements & {"farm", "mine", "saw"})
                and kind not in tile.improvements
                and player.prod >= info["cost"]
            )
            if allowed:
                button.enable()
            else:
                button.disable()
        self.build_panel.show()

    def hide_build_options(self) -> None:
        self.build_panel.hide()

    def contains_point(self, pos: tuple[int, int]) -> bool:
        """Return True if ``pos`` is over any HUD element.

        Includes the expanded buy-unit menu which may overlap the map area.
        """
        if self.rect.collidepoint(pos) or self.buy_unit.rect.collidepoint(pos):
            return True
        for menu in (self.buy_unit.current_state,):
            if menu is None:
                continue
            selected_button = getattr(menu, "selected_option_button", None)
            if selected_button and selected_button.rect.collidepoint(pos):
                return True
            options_list = getattr(menu, "options_selection_list", None)
            if options_list and options_list.rect.collidepoint(pos):
                return True
            close_button = getattr(menu, "close_button", None)
            if close_button and close_button.rect.collidepoint(pos):
                return True
        return False
