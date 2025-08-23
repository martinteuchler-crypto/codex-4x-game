TILE_SIZE = 32
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
