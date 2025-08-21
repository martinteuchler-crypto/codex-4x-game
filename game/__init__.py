"""Codex 4X game package with pygame compatibility helpers."""

# Some environments ship an older pygame lacking text-direction constants
# required by pygame_gui. Define them if missing so the UI can import
# successfully. Upstream pygame 2.6+ exposes these attributes.
import pygame

if not hasattr(pygame, "DIRECTION_LTR"):
    pygame.DIRECTION_LTR = 0
    pygame.DIRECTION_RTL = 1
