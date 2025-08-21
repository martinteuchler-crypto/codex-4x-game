from __future__ import annotations

from random import Random

from .. import config
from . import rules
from .models import State


def ai_take_turn(state: State, rng: Random) -> None:
    player_id = 1
    # buy unit if possible
    for city in state.cities.values():
        if city.owner == player_id:
            for kind in ("soldier", "scout"):
                cost = config.UNIT_STATS[kind]["cost"]
                if state.players[player_id].prod >= cost:
                    try:
                        rules.buy_unit(state, city.id, kind)
                    except rules.RuleError:
                        pass
            break
    # move units
    for unit in list(state.units.values()):
        if unit.owner != player_id:
            continue
        # try found city
        try:
            rules.found_city(state, unit.id)
            continue
        except rules.RuleError:
            pass
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        rng.shuffle(dirs)
        for dx, dy in dirs:
            dest = (unit.pos[0] + dx, unit.pos[1] + dy)
            if dest in state.tiles:
                try:
                    rules.move_unit(state, unit.id, dest)
                    break
                except rules.RuleError:
                    continue


__all__ = ["ai_take_turn"]
