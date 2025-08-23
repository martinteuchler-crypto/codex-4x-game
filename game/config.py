"""Global configuration values.

This module intentionally keeps only simple data and utility helpers so other
parts of the game can remain pure and easily testable.  ``TILE_SIZE`` used to be
treated as a fixed constant, but the UI now allows the window to be resized and
the map needs to scale accordingly.  To support dynamic scaling, helper
functions below expose a small API for updating ``TILE_SIZE`` in a controlled
way.
"""

TILE_SIZE: int = 32
UI_BAR_H = 64
MOVE_COST = {"plains": 1, "forest": 2, "hill": 2, "water": 999}
YIELD = {
    "plains": (1, 1),
    "forest": (0, 2),
    "hill": (0, 2),
    "water": (1, 0),
}
UNIT_STATS = {
    "scout": {"moves": 3, "food": 0, "prod": 3},
    "soldier": {"moves": 2, "food": 0, "prod": 4},
    "settler": {"moves": 2, "food": 2, "prod": 1},
}
INFRASTRUCTURE = {
    "farm": {
        "cost": 2,
        "yield": (1, 0),
        "required": {"plains"},
        "road_bonus": (1, 0),
    },
    "mine": {
        "cost": 2,
        "yield": (0, 1),
        "required": {"hill"},
        "road_bonus": (0, 1),
    },
    "saw": {
        "cost": 2,
        "yield": (0, 1),
        "required": {"forest"},
        "road_bonus": (0, 1),
    },
    "road": {
        "cost": 2,
        "yield": (0, 0),
        "required": {"plains", "forest", "hill"},
        "road_bonus": (0, 0),
    },
}
REVEAL_RADIUS = 3
START_SIZE = (20, 12)

# Window size limits
MIN_WINDOW = (640, 480)
MAX_WINDOW = (1920, 1280)


def clamp_window_size(size: tuple[int, int]) -> tuple[int, int]:
    """Clamp ``size`` to the allowed window bounds."""
    width = max(MIN_WINDOW[0], min(size[0], MAX_WINDOW[0]))
    height = max(MIN_WINDOW[1], min(size[1], MAX_WINDOW[1]))
    return width, height


def compute_tile_size(window: tuple[int, int], map_size: tuple[int, int]) -> int:
    """Return a tile size that fits ``map_size`` within ``window``.

    The HUD occupies ``UI_BAR_H`` pixels at the bottom of the screen, so only
    the remaining vertical space is available for the map.  The tile size is the
    largest integer that allows the entire map to be displayed without cropping.
    """

    width, height = window
    map_w, map_h = map_size
    available_h = max(1, height - UI_BAR_H)
    size_w = width // map_w
    size_h = available_h // map_h
    return max(1, min(size_w, size_h))


def set_tile_size(size: int) -> None:
    """Update ``TILE_SIZE`` to ``size`` ensuring it stays positive."""

    global TILE_SIZE
    TILE_SIZE = max(1, int(size))
