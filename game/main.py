from __future__ import annotations

import os

# Allow headless execution in CI or tests
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from .core.models import City, Player
from .ui.hud import ResourceHUD


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()

    player = Player(
        food=10,
        production=5,
        cities=[
            City((0, 0), food_yield=2, prod_yield=1),
            City((1, 1), food_yield=1, prod_yield=2),
        ],
    )
    hud = ResourceHUD(player)

    running = True
    frame = 0
    while running and frame < 5:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        hud.render(screen)
        pygame.display.flip()
        clock.tick(60)
        frame += 1

    pygame.quit()


if __name__ == "__main__":
    main()
