"""Research and tech tree helpers."""

from __future__ import annotations

from typing import Tuple

from .models import Player, State
from ..config import BASE_YIELD, COLONY_YIELD_BONUS, TECH_DEFS


def get_research_income(state: State, player_id: int) -> int:
    player = state.players[player_id]
    income = 0
    for cid in player.cities:
        city = state.cities[cid]
        tile = next(t for t in state.tiles if (t.x, t.y) == city.pos)
        base = BASE_YIELD[tile.kind]
        if city.role == "colony" and tile.habitable:
            bonus = COLONY_YIELD_BONUS
        else:
            bonus = (0, 0, 0)
        income += base[2] + bonus[2]
    return income


def can_research(player: Player, tech_id: str) -> Tuple[bool, str]:
    tech = TECH_DEFS[tech_id]
    for req in tech.get("requires", []):
        if req == "any:T1":
            if not any(
                TECH_DEFS[t]["tier"] == 1 and t in player.tech_unlocked
                for t in TECH_DEFS
            ):
                return False, "Requires any tier 1 tech"
        elif req not in player.tech_unlocked:
            return False, f"Requires {req}"
    return True, ""


def apply_research_income(state: State, player_id: int) -> State:
    player = state.players[player_id]
    income = get_research_income(state, player_id)
    player.research += income
    if player.active_tech:
        tech = TECH_DEFS[player.active_tech]
        progress = player.tech_progress.get(player.active_tech, 0) + player.research
        if progress >= tech["cost"]:
            player.tech_unlocked.add(player.active_tech)
            player.tech_progress[player.active_tech] = tech["cost"]
            player.research = progress - tech["cost"]
            player.active_tech = None
        else:
            player.tech_progress[player.active_tech] = progress
            player.research = 0
    return state
