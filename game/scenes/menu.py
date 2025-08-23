"""Menu scene."""

from __future__ import annotations

import pygame
import pygame_gui

from .. import config
from ..core import mapgen
from ..core.models import Player, State
from .gameplay import Gameplay


class Menu:
    def __init__(self) -> None:
        size = pygame.display.get_surface().get_size()
        self.manager = pygame_gui.UIManager(size)
        self.new = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text="New Game",
            manager=self.manager,
        )
        self.quit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text="Quit",
            manager=self.manager,
        )
        self._layout(size)

    def _layout(self, size: tuple[int, int]) -> None:
        center_x = size[0] // 2 - 50
        center_y = size[1] // 2
        self.new.set_relative_position((center_x, center_y - 60))
        self.quit.set_relative_position((center_x, center_y + 10))

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    new_size = config.clamp_window_size((event.w, event.h))
                    pygame.display.set_mode(new_size, pygame.RESIZABLE)
                    self.manager.set_window_resolution(new_size)
                    self._layout(new_size)
                elif (
                    event.type == pygame.USEREVENT
                    and event.user_type == pygame_gui.UI_BUTTON_PRESSED
                ):
                    if event.ui_element == self.new:
                        tiles, spawns = mapgen.generate_map(*config.START_SIZE, seed=1)
                        units = {u.id: u for u in mapgen.initial_units(spawns)}
                        players = {0: Player(0), 1: Player(1)}
                        state = State(
                            width=config.START_SIZE[0],
                            height=config.START_SIZE[1],
                            tiles=tiles,
                            units=units,
                            cities={},
                            players=players,
                        )
                        state.next_unit_id = max(units) + 1
                        for unit in state.units.values():
                            unit.moves_left = config.UNIT_STATS[unit.kind]["moves"]
                            for x in range(state.width):
                                for y in range(state.height):
                                    if (
                                        abs(unit.pos[0] - x) + abs(unit.pos[1] - y)
                                        <= config.REVEAL_RADIUS
                                    ):
                                        tile = state.tile_at((x, y))
                                        tile.revealed_by.add(unit.owner)
                        game = Gameplay(state)
                        game.run()
                    elif event.ui_element == self.quit:
                        running = False
                self.manager.process_events(event)
            self.manager.update(time_delta)
            surface = pygame.display.get_surface()
            surface.fill((0, 0, 0))
            self.manager.draw_ui(surface)
            pygame.display.flip()
