from __future__ import annotations

from random import Random
from typing import Optional, Tuple

from .. import config
from . import mapgen
from .models import City, Coord, Player, State, Tile, Unit


class RuleError(Exception):
    pass


def new_game(w: int, h: int, seed: int) -> State:
    tiles, spawns = mapgen.generate_map(w, h, seed)
    units_list = mapgen.initial_units(spawns)
    players = {i: Player(i) for i in range(len(spawns))}
    state = State(w, h, tiles, {}, {}, players)
    for u in units_list:
        u.id = state.gen_id()
        state.units[u.id] = u
        reveal(state, u.owner, u.pos)
    return state


def tile_at(state: State, pos: Coord) -> Tile:
    return state.tiles[pos]


def reveal(state: State, owner: int, pos: Coord) -> None:
    r = config.REVEAL_RADIUS
    px, py = pos
    for y in range(py - r, py + r + 1):
        for x in range(px - r, px + r + 1):
            if (x, y) in state.tiles:
                state.tiles[(x, y)].revealed_by.add(owner)


def move_unit(state: State, uid: int, dest: Coord) -> None:
    unit = state.units[uid]
    tile = tile_at(state, dest)
    cost = config.MOVE_COST[tile.kind]
    if cost > unit.moves_left:
        raise RuleError("not enough moves")
    # check friendly occupancy
    for other in state.units.values():
        if other.pos == dest:
            if other.owner == unit.owner:
                raise RuleError("tile occupied")
            else:  # combat
                del state.units[other.id]
                break
    # city capture
    for city in list(state.cities.values()):
        if city.pos == dest and city.owner != unit.owner:
            if unit.kind != "soldier":
                raise RuleError("need soldier to capture city")
            city.owner = unit.owner
    unit.pos = dest
    unit.moves_left -= cost
    reveal(state, unit.owner, dest)


def found_city(state: State, uid: int) -> int:
    unit = state.units[uid]
    tile = tile_at(state, unit.pos)
    if tile.kind == "water":
        raise RuleError("cannot found on water")
    if unit.owner not in tile.revealed_by:
        raise RuleError("tile not revealed")
    cid = state.gen_id()
    state.cities[cid] = City(cid, unit.owner, unit.pos)
    del state.units[uid]
    return cid


def buy_unit(state: State, city_id: int, kind: str) -> int:
    city = state.cities[city_id]
    player = state.players[city.owner]
    cost = config.UNIT_STATS[kind]["cost"]
    if player.prod < cost:
        raise RuleError("not enough production")
    # check occupancy
    for u in state.units.values():
        if u.pos == city.pos and u.owner != city.owner:
            raise RuleError("enemy occupying")
    player.prod -= cost
    uid = state.gen_id()
    unit = Unit(uid, city.owner, kind, city.pos, config.UNIT_STATS[kind]["moves"])
    state.units[uid] = unit
    reveal(state, unit.owner, unit.pos)
    return uid


def end_turn(state: State, rng: Random) -> None:
    # yields
    for city in state.cities.values():
        player = state.players[city.owner]
        fx, px = city_yield(state, city.pos)
        player.food += fx
        player.prod += px
    # reset moves
    for unit in state.units.values():
        unit.moves_left = config.UNIT_STATS[unit.kind]["moves"]
    state.current = 1 - state.current
    state.turn += 1


def city_yield(state: State, pos: Coord) -> Tuple[int, int]:
    x, y = pos
    food = 0
    prod = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (x + dx, y + dy) in state.tiles:
                f, p = config.YIELD[state.tiles[(x + dx, y + dy)].kind]
                food += f
                prod += p
    return food, prod


def check_win(state: State) -> Optional[int]:
    owners = {c.owner for c in state.cities.values()}
    if len(owners) == 1 and owners:
        return owners.pop()
    return None


__all__ = [
    "RuleError",
    "new_game",
    "tile_at",
    "move_unit",
    "found_city",
    "buy_unit",
    "end_turn",
    "check_win",
    "reveal",
]
