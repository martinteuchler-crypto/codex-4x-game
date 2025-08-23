"""Translate input events into game actions."""

from __future__ import annotations

from random import Random

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
        self.hud.focus.disable()
        self.hud.hide_message()

    def handle_event(
        self, event: pygame.event.Event, state: State, rng: Random
    ) -> None:
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
            self.hud.focus.disable()
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            # Ignore motion outside the map area or over the HUD (including the
            # expanded buy-unit dropdown) to prevent hover info from
            # interfering with HUD interactions.
            map_rect = pygame.Rect(
                0, 0, state.width * config.TILE_SIZE, state.height * config.TILE_SIZE
            )
            if not map_rect.collidepoint(x, y) or self.hud.contains_point((x, y)):
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
                    total_food = 0
                    total_prod = 0
                    for c in city.claimed:
                        food, prod = config.YIELD[state.tile_at(c).kind]
                        total_food += food
                        total_prod += prod
                    text = f"City (Player {city.owner}) F:{total_food} P:{total_prod}"
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
            if self.hud.contains_point((x, y)) or not map_rect.collidepoint(x, y):
                # Clicking HUD or outside the map should not affect selection.
                return
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            if (
                pygame.key.get_mods() & pygame.KMOD_SHIFT
                and self.selected is not None
                and self.selected in state.units
            ):
                src = state.units[self.selected].pos
                stack = [
                    u
                    for u in state.units.values()
                    if (
                        u.pos == src
                        and u.owner == state.current_player
                        and u.kind == "soldier"
                    )
                ]
                dx = abs(tile[0] - src[0])
                dy = abs(tile[1] - src[1])
                cost = config.MOVE_COST[state.tile_at(tile).kind]
                if max(dx, dy) != 1 or any(u.moves_left < cost for u in stack):
                    self.hud.show_message("Cannot move stack")
                else:
                    for u in list(stack):
                        try:
                            rules.move_unit(state, u.id, tile)
                        except rules.RuleError as e:
                            self.hud.show_message(str(e))
                            break
                    else:
                        self.hud.hide_message()
                return
            self.selected = None
            self.selected_city = None
            self.hud.buy_unit.disable()
            self.hud.focus.disable()
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
                    self.hud.focus.enable()
                    self.hud.set_focus_option(
                        "Food" if city.focus == "food" else "Production"
                    )
                else:
                    self.hud.focus.disable()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            x, y = event.pos
            map_rect = pygame.Rect(
                0, 0, state.width * config.TILE_SIZE, state.height * config.TILE_SIZE
            )
            if self.hud.contains_point((x, y)) or not map_rect.collidepoint(x, y):
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
                self.selected is not None
                and self.selected in state.units
                and event.key in {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4}
            ):
                kind = {
                    pygame.K_1: "farm",
                    pygame.K_2: "mine",
                    pygame.K_3: "saw",
                    pygame.K_4: "road",
                }[event.key]
                try:
                    rules.build_infrastructure(state, self.selected, kind)
                    self.hud.hide_message()
                except rules.RuleError as e:
                    self.hud.show_message(str(e))
            elif (
                event.key == pygame.K_f
                and self.selected is not None
                and self.selected in state.units
                and state.units[self.selected].kind == "settler"
            ):
                try:
                    city = rules.found_city(state, self.selected, rng)
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
                        city = rules.found_city(state, self.selected, rng)
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
                        self.hud.focus.disable()
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
            elif (
                event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                and event.ui_element == self.hud.focus
                and self.selected_city is not None
            ):
                city = state.cities[self.selected_city]
                city.focus = "food" if event.text == "Food" else "prod"
