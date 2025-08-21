"""Entry point for the game."""

from __future__ import annotations

import pygame
import pygame_gui

from .config import START_SIZE, TILE_SIZE, UI_BAR_H
from .scenes import gameplay, menu


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(
        (START_SIZE[0] * TILE_SIZE, START_SIZE[1] * TILE_SIZE + UI_BAR_H)
    )
    pygame.display.set_caption("Codex 4X")
    manager = pygame_gui.UIManager(screen.get_size())

    state = menu.run_menu(screen, manager)
    if state:
        gameplay.run_game(screen, manager, state)

    pygame.quit()


if __name__ == "__main__":
    main()
