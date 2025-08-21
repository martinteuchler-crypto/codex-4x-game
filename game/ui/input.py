from __future__ import annotations

import pygame

from .. import config
from ..core import rules
from ..core.models import State


class InputHandler:
    def __init__(self) -> None:
        self.selected: int | None = None

    def handle(self, event: pygame.event.Event, state: State) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            tile = (x // config.TILE_SIZE, y // config.TILE_SIZE)
            if event.button == 1:  # select
                self.selected = None
                for u in state.units.values():
                    if u.pos == tile and u.owner == state.current:
                        self.selected = u.id
                        break
            elif event.button == 3 and self.selected is not None:
                try:
                    rules.move_unit(state, self.selected, tile)
                except rules.RuleError:
                    pass


__all__ = ["InputHandler"]
