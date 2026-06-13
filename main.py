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

# ui helper classes

# button class
class Button:
    def __init__(self, rect, text, action_id, active_color=COLOR_ACCENT_CYAN, toggle_state=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action_id = action_id
        self.active_color = active_color
        self.is_hovered = False
        self.toggle_state = toggle_state  # toggle switch (True/False)

    def draw(self, surface, font):
        # Determine background and border colors based on state
        if self.toggle_state is not None:
            border_color = self.active_color if self.toggle_state else COLOR_HUD_BORDER
            bg_color = (self.active_color[0]//5, self.active_color[1]//5, self.active_color[2]//5) if self.toggle_state else (12, 18, 30)
        else:
            border_color = self.active_color if self.is_hovered else COLOR_HUD_BORDER
            bg_color = (self.active_color[0]//8, self.active_color[1]//8, self.active_color[2]//8) if self.is_hovered else (12, 18, 30)

        # Draw button box
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 1)

        # Draw decorative corner ticks for the sci-fi look
        if self.is_hovered or (self.toggle_state is True):
            tick_len = 5
            pygame.draw.line(surface, self.active_color, (self.rect.left, self.rect.top), (self.rect.left + tick_len, self.rect.top), 2)
            pygame.draw.line(surface, self.active_color, (self.rect.left, self.rect.top), (self.rect.left, self.rect.top + tick_len), 2)
            pygame.draw.line(surface, self.active_color, (self.rect.right - 1, self.rect.bottom - 1), (self.rect.right - 1 - tick_len, self.rect.bottom - 1), 2)
            pygame.draw.line(surface, self.active_color, (self.rect.right - 1, self.rect.bottom - 1), (self.rect.right - 1, self.rect.bottom - 1 - tick_len), 2)

        # Draw text
        text_color = COLOR_TEXT_BRIGHT if (self.is_hovered or self.toggle_state) else COLOR_TEXT_MUTED
        txt_surface = font.render(self.text, True, text_color)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
