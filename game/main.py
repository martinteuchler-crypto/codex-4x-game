from __future__ import annotations

import pygame

from .scenes.menu import Menu


def main() -> None:
    pygame.init()
    Menu().run()
    pygame.quit()


if __name__ == "__main__":
    main()
