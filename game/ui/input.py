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
        self.hud.end_turn.disable()
        self.hud.show_message("Found a city to end your turn")

    def handle_event(self, event: pygame.event.Event, state: State) -> None:
        self.hud.process_event(event)
        if self.selected is not None and self.selected not in state.units:
            self.selected = None
            self.hud.found_city.disable()
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            if (
                y >= state.height * config.TILE_SIZE
                or x < 0
                or x >= state.width * config.TILE_SIZE
            ):
                self.hud.clear_hover_info()
                return
            coord = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            units = state.units_at(coord)
            if units:
                unit = units[0]
                text = f"{unit.kind} (Player {unit.owner})"
            else:
                city = state.city_at(coord)
                if city is not None:
                    text = f"City (Player {city.owner})"
                else:
                    tile = state.tile_at(coord)
                    food, prod = config.YIELD[tile.kind]
                    text = f"{tile.kind} F:{food} P:{prod}"
            self.hud.set_hover_info(text)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if y >= state.height * config.TILE_SIZE:
                return
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
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
                except KeyError:
                    self.hud.show_message("Cannot move there")
            else:
                self.selected = None
                self.hud.found_city.disable()
                self.hud.show_message("No unit selected")
        elif event.type == pygame.KEYDOWN:
            if (
                self.selected is not None
                and self.selected in state.units
                and event.key in {pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d}
            ):
                unit = state.units[self.selected]
                dx, dy = {
                    pygame.K_w: (0, -1),
                    pygame.K_s: (0, 1),
                    pygame.K_a: (-1, 0),
                    pygame.K_d: (1, 0),
                }[event.key]
                dest = (unit.pos[0] + dx, unit.pos[1] + dy)
                try:
                    rules.move_unit(state, self.selected, dest)
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
                except KeyError:
                    self.hud.show_message("Cannot move there")
            elif (
                event.key == pygame.K_f
                and self.selected is not None
                and self.selected in state.units
                and state.units[self.selected].kind == "settler"
            ):
                try:
                    rules.found_city(state, self.selected)
                    self.selected = None
                    self.hud.found_city.disable()
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
                    self.selected = None
                    self.hud.found_city.disable()
                except KeyError:
                    self.hud.show_message("Cannot found city")
                    self.selected = None
                    self.hud.found_city.disable()
            elif event.key == pygame.K_RETURN:
                rules.end_turn(state)
                self.hud.hide_message()
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hud.end_turn:
                    rules.end_turn(state)
                    self.hud.hide_message()
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
                        self.hud.hide_message()
                    except rules.RuleError as e:
                        self.hud.show_message(str(e))
                        self.selected = None
                        self.hud.found_city.disable()
                    except KeyError:
                        self.hud.show_message("Cannot found city")
                        self.selected = None
                        self.hud.found_city.disable()

                elif event.ui_element == self.hud.buy_scout:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "scout")
                                self.hud.hide_message()
                            except rules.RuleError as e:
                                self.hud.show_message(str(e))
                            except KeyError:
                                self.hud.show_message("Cannot buy unit")
                            break
                elif event.ui_element == self.hud.buy_soldier:
                    for city in state.cities.values():
                        if city.owner == state.current_player:
                            try:
                                rules.buy_unit(state, city.id, "soldier")
                                self.hud.hide_message()
                            except rules.RuleError as e:
                                self.hud.show_message(str(e))
                            except KeyError:
                                self.hud.show_message("Cannot buy unit")
                            break
