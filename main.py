import pygame
import sys
import math
import random
from nasa_api import NASADataFetcher
from navigator import AStarGrid, Node

# configuration and constraints
# set grid size
GRID_SIZE = 50

# Predefined coordinates
START_COORDS = (5, 5)
END_COORDS = (34, 34)

# Color Palettes (Sleek Sci-Fi Theme)
COLOR_BG = (10, 12, 20)           # Deep space dark blue
COLOR_GRID = (25, 35, 50)         # Radar grid lines
COLOR_GRID_ACTIVE = (40, 60, 85)  # Radar lines under sweep
COLOR_TEXT_BRIGHT = (220, 240, 255) # Ice blue text
COLOR_TEXT_MUTED = (110, 130, 160)  # Muted grey-blue text
COLOR_HUD_PANEL = (15, 22, 36)     # Dashboard background
COLOR_HUD_BORDER = (35, 55, 85)    # Neon cyan-blue borders
COLOR_ACCENT_CYAN = (0, 230, 255)  # Spaceship, primary path, cyan buttons
COLOR_ACCENT_GREEN = (0, 255, 120) # Start planet (Earth), safe zones, success
COLOR_ACCENT_MAGENTA = (255, 0, 128) # End planet (Mars), targets
COLOR_ACCENT_RED = (255, 60, 60)     # Asteroids, hazardous targets, alarms
COLOR_ACCENT_AMBER = (255, 180, 0)   # Hazard warning borders
COLOR_CLOSED_LIST = (255, 60, 60, 45) # A* Search space overlays (with alpha)
COLOR_OPEN_LIST = (0, 255, 120, 45)   # A* Search space overlays (with alpha)
