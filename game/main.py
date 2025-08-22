"""Entry point for the 4X game."""

from __future__ import annotations

import pygame

from .scenes.menu import Menu


def main() -> None:
    pygame.init()
    size = (640, 480)
    pygame.display.set_mode(size)
    Menu().run()
    pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    main()
