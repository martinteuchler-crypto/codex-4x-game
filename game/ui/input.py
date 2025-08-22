"""Translate input events into game actions."""

from __future__ import annotations

import pygame
import pygame_gui

from .. import config
from ..core import rules
from ..core.models import State
from .hud import HUD


class InputHandler:
    def __init__(self, hud: HUD) -> None:
        self.hud = hud
        self.selected: int | None = None
        self.hud.found_city.disable()

    def handle_event(self, event: pygame.event.Event, state: State) -> None:
        self.hud.process_event(event)
        if self.selected is not None and self.selected not in state.units:
            self.selected = None
            self.hud.found_city.disable()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            self.selected = None
            for unit in state.units.values():
                if unit.pos == tile and unit.owner == state.current_player:
                    self.selected = unit.id
                    break
            if (
                self.selected is not None
                and self.selected in state.units
                and state.units[self.selected].kind == "settler"
            ):
                self.hud.found_city.enable()
            else:
                self.hud.found_city.disable()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.selected is not None and self.selected in state.units:
                x, y = event.pos
                dest = (x // config.TILE_SIZE, y // config.TILE_SIZE)
                try:
                    rules.move_unit(state, self.selected, dest)
                except (rules.RuleError, KeyError):
                    pass
            else:
                self.selected = None
                self.hud.found_city.disable()
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hud.end_turn:
                    rules.end_turn(state)
                elif (
                    event.ui_element == self.hud.found_city
                    and self.selected is not None
                    and self.selected in state.units
                    and state.units[self.selected].kind == "settler"
                ):
                    try:
                        rules.found_city(state, self.selected)
                        self.selected = None
                        self.hud.found_city.disable()
                    except (rules.RuleError, KeyError):
                        self.selected = None
                        self.hud.found_city.disable()
                elif event.ui_element == self.hud.buy_scout:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "scout")
                            except (rules.RuleError, KeyError):
                                pass
                            break
                elif event.ui_element == self.hud.buy_soldier:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "soldier")
                            except (rules.RuleError, KeyError):
                                pass
                            break
