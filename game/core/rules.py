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


def tile_yield(state: State, coord: Coord) -> tuple[int, int]:
    tile = state.tile_at(coord)
    food, prod = config.YIELD[tile.kind]
    for imp in tile.improvements:
        data = config.INFRASTRUCTURE[imp]
        f_bonus, p_bonus = data["yield"]
        food += f_bonus
        prod += p_bonus
    if "road" in tile.improvements:
        for imp in tile.improvements:
            if imp == "road":
                continue
            f_bonus, p_bonus = config.INFRASTRUCTURE[imp]["road_bonus"]
            food += f_bonus
            prod += p_bonus
    return food, prod


def grow_city(state: State, city: City, rng: Random) -> bool:
    """Attempt to grow ``city``.

    Returns ``True`` if the city grew and claimed a new tile, otherwise
    ``False``. Growth costs ``2 ** city.size`` food. The new tile is chosen
    among the unclaimed tiles nearest to the city, preferring those with the
    most already-claimed neighbours. Ties are resolved deterministically using
    ``rng.choice`` on a sorted list of candidates.
    """

    player = state.players[city.owner]
    cost = 2**city.size
    if (
        player.food < cost
        or city.last_grow_turn == state.turn
        or not claim_best_tile(state, city, rng)
    ):
        return False

    player.food -= cost
    city.size += 1
    city.last_grow_turn = state.turn
    return True


def move_unit(state: State, unit_id: int, dest: Coord) -> None:
    unit = state.units[unit_id]
    if unit.owner != state.current_player:
        raise RuleError("not your unit")
    if not in_bounds(state, dest):
        raise RuleError("out of bounds")
    dx = abs(dest[0] - unit.pos[0])
    dy = abs(dest[1] - unit.pos[1])
    if max(dx, dy) != 1:
        raise RuleError("must move to adjacent tile")
    tile = state.tile_at(dest)
    cost = config.MOVE_COST[tile.kind]
    if "road" in tile.improvements:
        cost = max(1, cost // 2)
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


def build_infrastructure(state: State, coord: Coord, kind: str) -> None:
    tile = state.tile_at(coord)
    owned_city = None
    for city in state.cities.values():
        if coord in city.claimed and city.owner == state.current_player:
            owned_city = city
            break
    if owned_city is None:
        raise RuleError("tile not claimed")
    info = config.INFRASTRUCTURE.get(kind)
    if info is None:
        raise RuleError("unknown infrastructure")
    if tile.kind not in info["required"]:
        raise RuleError("cannot build here")
    non_road = {k for k in config.INFRASTRUCTURE if k != "road"}
    if kind != "road" and tile.improvements & non_road:
        raise RuleError("infrastructure exists")
    if kind in tile.improvements:
        raise RuleError("infrastructure exists")
    player = state.players[state.current_player]
    cost = info["cost"]
    if player.prod < cost:
        raise RuleError("not enough production")
    player.prod -= cost
    tile.improvements.add(kind)


def claim_best_tile(state: State, city: City, rng: Random) -> bool:
    claimed_tiles = {coord for c in state.cities.values() for coord in c.claimed}
    unclaimed = [
        (x, y)
        for x in range(state.width)
        for y in range(state.height)
        if (x, y) not in claimed_tiles
        and city.owner in state.tile_at((x, y)).revealed_by
    ]
    if not unclaimed:
        return False

    min_dist = min(distance(city.pos, c) for c in unclaimed)
    nearest = [c for c in unclaimed if distance(city.pos, c) == min_dist]

    def neighbour_count(coord: Coord) -> int:
        x, y = coord
        neighbours = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return sum(1 for n in neighbours if n in city.claimed)

    max_neigh = max(neighbour_count(c) for c in nearest)
    candidates = [c for c in nearest if neighbour_count(c) == max_neigh]
    city.claimed.add(rng.choice(sorted(candidates)))
    return True


def end_turn(state: State, rng: Random | None = None) -> None:
    rng = rng or Random()
    for city in state.cities.values():
        if not city.claimed:
            city.claimed.add(city.pos)
        grow_city(state, city, rng)
        tiles = list(city.claimed)
        focus_idx = 0 if city.focus == "food" else 1
        tiles.sort(
            key=lambda c: tile_yield(state, c)[focus_idx],
            reverse=True,
        )
        limit = min(len(tiles), city.size + 1)
        selected = tiles[:limit]
        total_food = 0
        total_prod = 0
        for coord in selected:
            food, prod = tile_yield(state, coord)
            total_food += food
            total_prod += prod
        player = state.players[city.owner]
        player.food += total_food
        player.prod += total_prod

    state.current_player = 1 - state.current_player
    state.turn += 1
    for unit in state.units.values():
        if unit.owner == state.current_player:
            unit.moves_left = config.UNIT_STATS[unit.kind]["moves"]


def found_city(state: State, unit_id: int, rng: Random | None = None) -> City:

    unit = state.units[unit_id]
    if unit.kind != "settler":
        raise RuleError("only settlers can found cities")
    tile = state.tile_at(unit.pos)
    if tile.kind == "water":
        raise RuleError("cannot found on water")
    if state.city_at(unit.pos):
        raise RuleError("city exists")
    rng = rng or Random()
    reveal(state, unit)
    city = City(
        id=state.next_city_id,
        owner=unit.owner,
        pos=unit.pos,
        claimed={unit.pos},
    )
    city.claimed.add(city.pos)

    state.cities[city.id] = city
    state.next_city_id += 1
    del state.units[unit.id]

    claim_best_tile(state, city, rng)
    return city


def buy_unit(state: State, city_id: int, kind: str) -> Unit:
    city = state.cities[city_id]
    if city.owner != state.current_player:
        raise RuleError("not your city")
    if kind == "settler" and city.size < 2:
        raise RuleError("city too small")
    stats = config.UNIT_STATS[kind]
    cost_food = stats.get("food", 0)
    cost_prod = stats.get("prod", 0)
    player = state.players[city.owner]
    if player.food < cost_food or player.prod < cost_prod:
        raise RuleError("not enough resources")
    units_here = state.units_at(city.pos)
    if any(u.owner != city.owner for u in units_here):
        raise RuleError("tile occupied")
    if kind != "soldier" and units_here:
        raise RuleError("tile occupied")
    player.food -= cost_food
    player.prod -= cost_prod
    if kind == "settler":
        city.size -= 1
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
    "grow_city",
    "build_infrastructure",
    "tile_yield",
]
