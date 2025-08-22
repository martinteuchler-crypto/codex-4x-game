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

    def handle_event(self, event: pygame.event.Event, state: State) -> None:
        self.hud.process_event(event)
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            context = ""
            if 0 <= tile[0] < state.width and 0 <= tile[1] < state.height:
                for unit in state.units.values():
                    if unit.pos == tile:
                        context = f"{unit.kind.title()} (Player {unit.owner})"
                        break
                else:
                    for city in state.cities.values():
                        if city.pos == tile:
                            context = f"City (Player {city.owner})"
                            break
                    else:
                        tile_obj = state.tile_at(tile)
                        if state.current_player in tile_obj.revealed_by:
                            food, prod = config.YIELD[tile_obj.kind]
                            context = f"{tile_obj.kind.title()} F{food} P{prod}"
            self.hud.set_context(context)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            for unit in state.units.values():
                if unit.pos == tile and unit.owner == state.current_player:
                    self.selected = unit.id
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.selected is not None:
                x, y = event.pos
                dest = (x // config.TILE_SIZE, y // config.TILE_SIZE)
                try:
                    rules.move_unit(state, self.selected, dest)
                except rules.RuleError:
                    pass
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hud.end_turn:
                    rules.end_turn(state)
                elif (
                    event.ui_element == self.hud.found_city
                    and self.selected is not None
                ):
                    try:
                        rules.found_city(state, self.selected)
                        self.selected = None
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
