"""Input handling helpers."""

from __future__ import annotations

import pygame

from ..core.models import State
from ..core.rules import end_turn, move_unit


def handle_event(
    state: State, event: pygame.event.Event, selected: int | None
) -> int | None:
    if event.type == pygame.KEYDOWN:
        if selected is not None:
            unit = state.units[selected]
            if event.key == pygame.K_UP:
                move_unit(state, selected, (unit.pos[0], max(0, unit.pos[1] - 1)))
            elif event.key == pygame.K_DOWN:
                move_unit(
                    state,
                    selected,
                    (unit.pos[0], min(state.height - 1, unit.pos[1] + 1)),
                )
            elif event.key == pygame.K_LEFT:
                move_unit(state, selected, (max(0, unit.pos[0] - 1), unit.pos[1]))
            elif event.key == pygame.K_RIGHT:
                move_unit(
                    state,
                    selected,
                    (min(state.width - 1, unit.pos[0] + 1), unit.pos[1]),
                )
        if event.key == pygame.K_SPACE:
            end_turn(state)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        x, y = event.pos
        gx = x // 32
        gy = (y - 64) // 32
        for uid, unit in state.units.items():
            if (gx, gy) == unit.pos and unit.owner == state.current_player:
                selected = uid
                break
    return selected
