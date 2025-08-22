"""Gameplay scene."""

from __future__ import annotations

from random import Random

import pygame

from .. import config
from ..core import ai, mapgen
from ..core.models import Player, State
from ..core.rules import check_win
from ..ui.hud import HUD
from ..ui.input import InputHandler
from ..ui.renderer import draw


class Gameplay:
    def __init__(self, size: tuple[int, int], seed: int) -> None:
        tiles, spawns = mapgen.generate_map(*size, seed)
        units = {u.id: u for u in mapgen.initial_units(spawns)}
        players = {0: Player(0), 1: Player(1)}
        self.state = State(
            width=size[0],
            height=size[1],
            tiles=tiles,
            units=units,
            cities={},
            players=players,
        )
        for unit in self.state.units.values():
            unit.moves_left = config.UNIT_STATS[unit.kind]["moves"]
        self.screen = pygame.display.get_surface()
        self.hud = HUD(
            pygame.Rect(
                0,
                size[1] * config.TILE_SIZE,
                size[0] * config.TILE_SIZE,
                config.UI_BAR_H,
            )
        )
        self.input = InputHandler(self.hud)
        for unit in self.state.units.values():
            for x in range(self.state.width):
                for y in range(self.state.height):
                    if (
                        abs(unit.pos[0] - x) + abs(unit.pos[1] - y)
                        <= config.REVEAL_RADIUS
                    ):
                        self.state.tile_at((x, y)).revealed_by.add(unit.owner)

    def run(self) -> None:
        clock = pygame.time.Clock()
        rng = Random()
        running = True
        while running:
            time_delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.input.handle_event(event, self.state)
            if self.state.current_player == 1:
                ai.ai_turn(self.state, rng)
            self.hud.update(time_delta, self.state)
            draw(self.state, self.screen, self.input.selected)
            self.hud.draw(self.screen)
            pygame.display.flip()
            if check_win(self.state) is not None:
                running = False
