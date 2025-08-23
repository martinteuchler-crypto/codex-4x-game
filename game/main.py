"""Entry point for the 4X game."""

from __future__ import annotations

import pygame

from . import config
from .scenes.menu import Menu


def main() -> None:
    pygame.init()
    size = config.MIN_WINDOW
    pygame.display.set_mode(size, pygame.RESIZABLE)
    Menu().run()
    pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    main()
