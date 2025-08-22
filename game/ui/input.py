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
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            map_h = state.height * config.TILE_SIZE
            if y >= map_h:
                return
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            if event.button == 1:
                self.selected = None
                for unit in state.units.values():
                    if unit.pos == tile and unit.owner == state.current_player:
                        self.selected = unit.id
                        break
                if (
                    self.selected is not None
                    and state.units[self.selected].kind == "settler"
                ):
                    self.hud.found_city.enable()
                else:
                    self.hud.found_city.disable()
            elif event.button == 3 and self.selected is not None:
                try:
                    rules.move_unit(state, self.selected, tile)
                except rules.RuleError:
                    pass
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hud.end_turn:
                    rules.end_turn(state)
                elif (
                    event.ui_element == self.hud.found_city
                    and self.selected is not None
                    and state.units[self.selected].kind == "settler"
                ):
                    try:
                        rules.found_city(state, self.selected)
                        self.selected = None
                        self.hud.found_city.disable()
                    except rules.RuleError:
                        pass
                elif event.ui_element == self.hud.buy_scout:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "scout")
                            except rules.RuleError:
                                pass
                            break
                elif event.ui_element == self.hud.buy_soldier:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "soldier")
                            except rules.RuleError:
                                pass
                            break
