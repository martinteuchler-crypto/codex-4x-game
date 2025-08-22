import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.core.models import Player, State, Tile
from game.ui.hud import HUD


def make_state() -> State:
    tiles = [Tile(0, 0, "plains")]
    players = {
        0: Player(id=0, food=10, prod=5),
        1: Player(id=1, food=1, prod=2),
    }
    return State(1, 1, tiles, {}, {}, players, current_player=0)


def test_hud_switches_resource_display_with_current_player() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    hud = HUD(pygame.Rect(0, 0, 640, 480))
    state = make_state()

    hud.update(0.0, state)
    assert "F:10 P:5" in hud.info.text

    state.current_player = 1
    hud.update(0.0, state)
    assert "F:1 P:2" in hud.info.text
    pygame.quit()
