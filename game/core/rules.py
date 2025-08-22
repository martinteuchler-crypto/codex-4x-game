"""Game rules and turn engine."""

from __future__ import annotations

from random import Random

from .. import config
from .models import City, Coord, State, Unit


class RuleError(Exception):
    """Raised when an action is invalid."""


def in_bounds(state: State, coord: Coord) -> bool:
    x, y = coord
    return 0 <= x < state.width and 0 <= y < state.height


def distance(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reveal(state: State, unit: Unit) -> None:
    for x in range(state.width):
        for y in range(state.height):
            if distance((x, y), unit.pos) <= config.REVEAL_RADIUS:
                state.tile_at((x, y)).revealed_by.add(unit.owner)


def move_unit(state: State, unit_id: int, dest: Coord) -> None:
    unit = state.units[unit_id]
    if unit.owner != state.current_player:
        raise RuleError("not your unit")
    if not in_bounds(state, dest):
        raise RuleError("out of bounds")
    tile = state.tile_at(dest)
    cost = config.MOVE_COST[tile.kind]
    if cost > unit.moves_left:
        raise RuleError("not enough moves")
    unit.pos = dest
    unit.moves_left -= cost
    reveal(state, unit)
    for other in list(state.units.values()):
        if other is unit:
            continue
        if other.pos == dest and other.owner != unit.owner:
            del state.units[other.id]
    city = state.city_at(dest)
    if city and city.owner != unit.owner and unit.kind == "soldier":
        city.owner = unit.owner


def end_turn(state: State) -> None:
    for city in state.cities.values():
        food, prod = config.YIELD[state.tile_at(city.pos).kind]
        player = state.players[city.owner]
        player.food += food
        player.prod += prod
    state.current_player = 1 - state.current_player
    state.turn += 1
    for unit in state.units.values():
        if unit.owner == state.current_player:
            unit.moves_left = config.UNIT_STATS[unit.kind]["moves"]


def found_city(state: State, unit_id: int, rng: Random) -> City:
    unit = state.units[unit_id]
    if unit.kind != "settler":
        raise RuleError("only settlers can found cities")
    tile = state.tile_at(unit.pos)
    if tile.kind == "water":
        raise RuleError("cannot found on water")
    if state.city_at(unit.pos):
        raise RuleError("city exists")
    city = City(id=state.next_city_id, owner=unit.owner, pos=unit.pos)
    city.claimed.add(city.pos)
    state.cities[city.id] = city
    state.next_city_id += 1
    del state.units[unit.id]
    neighbors: list[Coord] = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        coord = (city.pos[0] + dx, city.pos[1] + dy)
        if not in_bounds(state, coord):
            continue
        if state.tile_at(coord).kind == "water":
            continue
        if any(coord in c.claimed for c in state.cities.values()):
            continue
        neighbors.append(coord)
    if neighbors:
        city.claimed.add(rng.choice(neighbors))
    return city


def buy_unit(state: State, city_id: int, kind: str) -> Unit:
    city = state.cities[city_id]
    if city.owner != state.current_player:
        raise RuleError("not your city")
    stats = config.UNIT_STATS[kind]
    cost_food = stats.get("food", 0)
    cost_prod = stats.get("prod", 0)
    player = state.players[city.owner]
    if player.food < cost_food or player.prod < cost_prod:
        raise RuleError("not enough resources")
    if state.units_at(city.pos):
        raise RuleError("tile occupied")
    player.food -= cost_food
    player.prod -= cost_prod
    unit = Unit(
        id=state.next_unit_id,
        owner=city.owner,
        kind=kind,
        pos=city.pos,
        moves_left=config.UNIT_STATS[kind]["moves"],
    )
    state.units[unit.id] = unit
    state.next_unit_id += 1
    reveal(state, unit)
    return unit


def check_win(state: State) -> int | None:
    """Return winning player if a side has no cities *and* no settlers."""
    city_owners = {city.owner for city in state.cities.values()}
    settler_owners = {
        unit.owner for unit in state.units.values() if unit.kind == "settler"
    }
    for player_id in state.players:
        if player_id not in city_owners and player_id not in settler_owners:
            return 1 - player_id
    return None


__all__ = [
    "RuleError",
    "move_unit",
    "end_turn",
    "found_city",
    "buy_unit",
    "check_win",
]
