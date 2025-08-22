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
        self.selected_city: int | None = None
        self.hud.found_city.disable()
        self.hud.buy_unit.disable()
        self.hud.hide_message()

    def handle_event(self, event: pygame.event.Event, state: State) -> None:
        self.hud.process_event(event)
        if self.selected is not None and self.selected not in state.units:
            self.selected = None
            self.hud.found_city.disable()
        if self.selected_city is not None and (
            self.selected_city not in state.cities
            or state.cities[self.selected_city].owner != state.current_player
        ):
            self.selected_city = None
            self.hud.buy_unit.disable()
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            # Ignore motion outside the map area, including over the HUD,
            # to prevent hover info from interfering with HUD interactions.
            map_rect = pygame.Rect(
                0, 0, state.width * config.TILE_SIZE, state.height * config.TILE_SIZE
            )
            if not map_rect.collidepoint(x, y):
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
            map_rect = pygame.Rect(
                0, 0, state.width * config.TILE_SIZE, state.height * config.TILE_SIZE
            )
            if self.hud.rect.collidepoint(x, y) or not map_rect.collidepoint(x, y):
                # Clicking HUD or outside the map should not affect selection.
                return
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            self.selected = None
            self.selected_city = None
            self.hud.buy_unit.disable()
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
                city = state.city_at(tile)
                if city and city.owner == state.current_player:
                    self.selected_city = city.id
                    self.hud.buy_unit.enable()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            x, y = event.pos
            map_rect = pygame.Rect(
                0, 0, state.width * config.TILE_SIZE, state.height * config.TILE_SIZE
            )
            if self.hud.rect.collidepoint(x, y) or not map_rect.collidepoint(x, y):
                return
            if self.selected is not None and self.selected in state.units:
                dest = (x // config.TILE_SIZE, y // config.TILE_SIZE)
                try:
                    rules.move_unit(state, self.selected, dest)
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
                except KeyError:
                    self.hud.show_message("Cannot move there")
            else:
                # Do not clear a selected city when right-clicking with no unit
                # selected so its claimed tiles remain highlighted.
                self.selected = None
                self.hud.found_city.disable()
                if self.selected_city is None:
                    self.hud.buy_unit.disable()
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
                    city = rules.found_city(state, self.selected)
                    self.selected = None
                    self.selected_city = city.id
                    self.hud.found_city.disable()
                    self.hud.buy_unit.enable()
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
                    self.selected = None
                    self.selected_city = None
                    self.hud.found_city.disable()
                    self.hud.buy_unit.disable()
                except KeyError:
                    self.hud.show_message("Cannot found city")
                    self.selected = None
                    self.selected_city = None
                    self.hud.found_city.disable()
                    self.hud.buy_unit.disable()
            elif event.key == pygame.K_RETURN:
                rules.end_turn(state)
                self.selected = None
                self.selected_city = None
                self.hud.found_city.disable()
                self.hud.buy_unit.disable()
                self.hud.hide_message()
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hud.end_turn:
                    rules.end_turn(state)
                    self.selected = None
                    self.selected_city = None
                    self.hud.found_city.disable()
                    self.hud.buy_unit.disable()
                    self.hud.hide_message()
                elif (
                    event.ui_element == self.hud.found_city
                    and self.selected is not None
                    and self.selected in state.units
                    and state.units[self.selected].kind == "settler"
                ):
                    try:
                        city = rules.found_city(state, self.selected)
                        self.selected = None
                        self.selected_city = city.id
                        self.hud.found_city.disable()
                        self.hud.buy_unit.enable()
                        self.hud.hide_message()
                    except rules.RuleError as e:
                        self.hud.show_message(str(e))
                        self.selected = None
                        self.selected_city = None
                        self.hud.found_city.disable()
                        self.hud.buy_unit.disable()
                    except KeyError:
                        self.hud.show_message("Cannot found city")
                        self.selected = None
                        self.selected_city = None
                        self.hud.found_city.disable()
                        self.hud.buy_unit.disable()
            elif (
                event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                and event.ui_element == self.hud.buy_unit
            ):
                if self.selected_city is not None and event.text != "Buy Unit":
                    kind = event.text.split()[-1].lower()
                    try:
                        rules.buy_unit(state, self.selected_city, kind)
                        self.hud.hide_message()
                    except rules.RuleError as e:
                        self.hud.show_message(str(e))
                    except KeyError:
                        self.hud.show_message("Cannot buy unit")
                self.hud.reset_buy_unit()
