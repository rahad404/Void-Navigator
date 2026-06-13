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

# cosmic object class
class CosmicObjectRenderer:
    """Handles rendering of various celestial bodies procedurally with glow layers."""
    @staticmethod
    def draw_planet(surface, cx, cy, radius, primary_color, atmosphere_color, name=""):
        # 1. Glow layer
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        for i in range(radius * 2, radius, -2):
            alpha = int(45 * (1.0 - (i - radius) / radius))
            pygame.draw.circle(glow_surf, (atmosphere_color[0], atmosphere_color[1], atmosphere_color[2], alpha), (radius*2, radius*2), i)
        surface.blit(glow_surf, (cx - radius*2, cy - radius*2))

        # 2. Base planet sphere
        pygame.draw.circle(surface, primary_color, (cx, cy), radius)

        # 3. Dynamic surface patterns (continents, storm bands)
        random.seed(name)  # Generate consistent surface structures based on the name
        pattern_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(pattern_surf, (255, 255, 255, 255), (radius, radius), radius)

        if "Earth" in name:
            # Draw continents on Earth
            for _ in range(5):
                continent_color = (34, 139, 34, 180) # Forest green
                px = radius + random.randint(-radius//2, radius//2)
                py = radius + random.randint(-radius//2, radius//2)
                pr = random.randint(radius//4, radius//2)
                pygame.draw.circle(pattern_surf, continent_color, (px, py), pr)
        else:
            # Draw storms/bands on Mars or other planets
            for _ in range(3):
                band_color = (primary_color[0]//2, primary_color[1]//2, primary_color[2]//2, 150)
                bx = radius
                by = radius + random.randint(-radius//2, radius//2)
                bw = random.randint(radius//2, radius)
                bh = random.randint(2, 5)
                pygame.draw.ellipse(pattern_surf, band_color, (bx - bw, by - bh//2, bw*2, bh))

        # Clip patterns to circular sphere
        sphere_mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(sphere_mask, (255, 255, 255, 255), (radius, radius), radius)
        pattern_surf.blit(sphere_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(pattern_surf, (cx - radius, cy - radius))

        # 4. Shadow/crescent overlay (3D volume effect)
        shadow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 140), (radius, radius), radius)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 0), (radius - radius//3, radius - radius//3), radius)
        surface.blit(shadow_surf, (cx - radius, cy - radius))

    @staticmethod
    def draw_asteroid(surface, cx, cy, radius, details):
        # Asteroids are jagged irregular polygons
        num_points = 8
        points = []
        random.seed(details["id"])

        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            r_offset = random.randint(-int(radius*0.25), int(radius*0.25))
            r = max(3, radius + r_offset)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))

        color = (139, 115, 85) if not details.get("is_hazardous") else (210, 80, 80)
        # Inner fill
        pygame.draw.polygon(surface, (color[0]//2, color[1]//2, color[2]//2), points)
        # Outer wireframe contour
        pygame.draw.polygon(surface, color, points, 1)

        # Draw a small asteroid glow if hazardous
        if details.get("is_hazardous"):
            glow = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 50, 50, 40), (radius*2, radius*2), radius*2)
            surface.blit(glow, (cx - radius*2, cy - radius*2))

    @staticmethod
    def draw_star(surface, cx, cy, spectral, cell_size):
        # Map spectral class to visual color and size
        char = spectral[0].upper() if spectral else 'G'
        star_map = {
            'O': ((180, 220, 255), 7, (130, 180, 255)), # Deep blue
            'B': ((200, 240, 255), 6, (150, 200, 255)), # Cyan-blue
            'A': ((255, 255, 255), 5, (200, 220, 255)), # Bright white
            'F': ((255, 255, 220), 5, (255, 255, 170)), # Yellow-white
            'G': ((255, 235, 150), 4, (255, 200, 100)), # Yellow (Sun)
            'K': ((255, 170, 80), 5, (255, 120, 50)),   # Orange giant
            'M': ((255, 90, 70), 8, (255, 50, 30))       # Red supergiant
        }
        color, base_radius, glow_color = star_map.get(char, star_map['G'])

        # Scale radius based on cell size to look nice on all window sizes
        scale_r = max(2, int(base_radius * (cell_size / 19.0)))

        # 1. Radiant pulsing glow
        pulse = 1.0 + 0.15 * math.sin(pygame.time.get_ticks() / 150.0)
        glow_radius = int(scale_r * 3.5 * pulse)
        glow = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (glow_color[0], glow_color[1], glow_color[2], 50), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow, (cx - glow_radius, cy - glow_radius))

        # 2. Main star body
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), scale_r)
        pygame.draw.circle(surface, color, (cx, cy), scale_r, 1)

    @staticmethod
    def draw_galaxy(surface, cx, cy, details, time_tick, cell_size):
        # Draw a beautiful rotating spiral galaxy
        random.seed(details["id"])
        num_arms = 2
        particles_per_arm = 25

        # Dynamic rotation speed based on ticks
        base_angle = (time_tick / 60.0) % (2 * math.pi)

        # Scale size dynamically
        gal_r = int(cell_size * 1.1)

        # Draw central nucleus glow
        nucleus_glow = pygame.Surface((gal_r*2, gal_r*2), pygame.SRCALPHA)
        pygame.draw.circle(nucleus_glow, (255, 180, 255, 60), (gal_r, gal_r), gal_r)
        surface.blit(nucleus_glow, (cx - gal_r, cy - gal_r))
        pygame.draw.circle(surface, (255, 230, 255), (cx, cy), max(2, cell_size//8))

        # Draw arm spirals using tiny dots
        for arm in range(num_arms):
            arm_phase = arm * math.pi
            for i in range(1, particles_per_arm):
                factor = i / float(particles_per_arm)
                dist = factor * gal_r * 1.15  # Arm extension radius
                spiral_angle = base_angle + arm_phase + (factor * 3.5) # Spiral curl rate

                # Add small dispersion dispersion
                disp_x = random.randint(-1, 1)
                disp_y = random.randint(-1, 1)

                px = cx + dist * math.cos(spiral_angle) + disp_x
                py = cy + dist * math.sin(spiral_angle) + disp_y

                # Color shifts from core (bright pink/white) to edge (cyan/blue)
                r = int(255 * (1.0 - factor) + 50 * factor)
                g = int(200 * (1.0 - factor) + 200 * factor)
                b = int(255)

                if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                    surface.set_at((int(px), int(py)), (r, g, b))

    @staticmethod
    def draw_nebula(surface, cx, cy, details, time_tick, cell_size):
        # Draw soft, overlapping gas clouds (using transparent circles)
        random.seed(details["id"])
        num_clouds = 4
        base_neb_r = int(cell_size * 0.95)

        for i in range(num_clouds):
            # Slow orbital drift of the cloud cells
            drift_angle = (time_tick / (100.0 + i*20.0)) + i * (math.pi/2.0)
            dx = (cell_size // 4) * math.cos(drift_angle)
            dy = (cell_size // 4) * math.sin(drift_angle)

            radius = random.randint(int(base_neb_r * 0.75), int(base_neb_r * 1.15))
            neb_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

            # Nebulae have magenta, purple, and green colors
            color_choice = i % 3
            if color_choice == 0:
                color = (255, 0, 150, 18)   # Magenta
            elif color_choice == 1:
                color = (130, 0, 255, 15)  # Purple
            else:
                color = (0, 255, 180, 12)  # Glowing teal-green

            pygame.draw.circle(neb_surf, color, (radius, radius), radius)
            surface.blit(neb_surf, (cx + dx - radius, cy + dy - radius))

# particle engine to generate thruster spark effect
class ParticleEngine:
    """Manages thruster spark particles emitted by the moving spaceship."""
    def __init__(self):
        self.particles = []

    def emit(self, x, y, dx, dy):
        """Creates new spark particles behind the ship."""
        for _ in range(3):
            self.particles.append({
                "x": x,
                "y": y,
                # Random velocity spraying opposite to ship movement
                "vx": -dx * 1.5 + random.uniform(-0.5, 0.5),
                "vy": -dy * 1.5 + random.uniform(-0.5, 0.5),
                "life": 1.0, # Decay life percentage (1.0 -> 0.0)
                "color": random.choice([COLOR_ACCENT_CYAN, (255, 150, 0), (255, 60, 0)]) # Cyan/orange sparks
            })

    def update(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.04
        # Filter dead particles
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface):
        for p in self.particles:
            size = max(1, int(p["life"] * 4))
            alpha = int(p["life"] * 255)
            # Create small surfaces for alpha blend
            p_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (p["color"][0], p["color"][1], p["color"][2], alpha), (size, size), size)
            surface.blit(p_surf, (p["x"] - size, p["y"] - size))

# main engine class
class VoidNavigatorApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Void Navigator - AI Pathfinding Dashboard")

        # Adjustable Window State - default is a compact size that fits all displays comfortably
        self.window_width = 1020
        self.window_height = 680
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Load fonts
        self.font_title = pygame.font.SysFont(["consolas", "monospace", "courier"], 20, bold=True)
        self.font_normal = pygame.font.SysFont(["consolas", "monospace", "courier"], 14)
        self.font_bold = pygame.font.SysFont(["consolas", "monospace", "courier"], 14, bold=True)
        self.font_hud = pygame.font.SysFont(["consolas", "monospace", "courier"], 11)

        # Core Engines Initialization
        self.fetcher = NASADataFetcher(grid_size=GRID_SIZE)
        self.grid_model = AStarGrid(size=GRID_SIZE)
        self.particles = ParticleEngine()

        # Application States
        self.current_stage = 1  # 1 = Asteroids, 2 = Deep Space
        self.start_node = START_COORDS
        self.end_node = END_COORDS
        self.active_path = None
        self.open_list_vis = set()
        self.closed_list_vis = set()

        # Toggles
        self.show_search_tree = True
        self.heuristic_mode = "octile" # octile, euclidean, manhattan
        self.mouse_mode = "start"      # "start" or "target" (defines what grid left-click does)

        # Radar Sweep Animation
        self.radar_angle = 0.0

        # Twinkle starfield background buffer (oversized to cover any screen expansions smoothly)
        self.stars_bg = [{"x": random.randint(0, 2560),
                          "y": random.randint(0, 1600),
                          "size": random.choice([1, 2]),
                          "twinkle_speed": random.uniform(0.02, 0.05),
                          "phase": random.uniform(0, math.pi * 2)} for _ in range(200)]

        # Spaceship animation state
        self.is_animating = False
        self.anim_index = 0
        self.ship_x = float(self.start_node[0])
        self.ship_y = float(self.start_node[1])
        self.ship_angle = 0.0
        self.ship_speed_mult = 0.15  # Traversal speed
        self.fuel_level = 100.0

        # Sensors Scan Details
        self.active_scanned_object = None
        self.hologram_rotation_angle = 0.0

        # Stage 1 Custom Planetary Stations (Not obstacles, acts as departures/destinations)
        self.stage_1_planets = [
            {"name": "Earth Station", "x": 5, "y": 5, "color": (60, 110, 200), "atmos": (80, 180, 255), "radius": 10},
            {"name": "Mars Colony", "x": 34, "y": 34, "color": (220, 90, 60), "atmos": (255, 130, 80), "radius": 9},
            {"name": "Mercury Outpost", "x": 12, "y": 25, "color": (120, 120, 120), "atmos": (150, 150, 150), "radius": 6},
            {"name": "Venus Observatory", "x": 22, "y": 12, "color": (225, 190, 130), "atmos": (245, 210, 150), "radius": 8},
            {"name": "Jupiter Research", "x": 32, "y": 8, "color": (205, 130, 80), "atmos": (225, 160, 110), "radius": 12},
            {"name": "Saturn Gateway", "x": 8, "y": 32, "color": (220, 200, 140), "atmos": (240, 220, 160), "radius": 10, "rings": True}
        ]

        # Load stage datasets
        self.asteroids_dataset = []
        self.deep_space_dataset = self.fetcher.deep_space_catalog

        # Calculate layout coordinates at startup
        self.update_layout_dimensions()

        # Fetch initial asteroid data
        self.reload_asteroids()
        self.calculate_path()

    # update layout dimention
    # Calculates sizing variables dynamically based on window width and height.
    def update_layout_dimensions(self):
        # Enforce minimum size boundary constraints to avoid UI collapse
        self.window_width = max(800, self.window_width)
        self.window_height = max(550, self.window_height)

        # Calculate dynamic grid bounding square area
        # Reserve 380px for the right side cockpit dashboard, and a 40px vertical margin buffer
        grid_area_size = min(self.window_width - 380, self.window_height - 40)
        self.cell_size = max(8, grid_area_size // GRID_SIZE)
        self.grid_display_size = self.cell_size * GRID_SIZE

        # Centering the grid vertically
        self.grid_margin_left = 20
        self.grid_margin_top = (self.window_height - self.grid_display_size) // 2

        # Sidebar coordinates
        self.sidebar_x = self.grid_margin_left + self.grid_display_size + 20
        self.sidebar_width = self.window_width - self.sidebar_x

        # Refresh button layouts
        self._build_ui_buttons()

    # reload astroid
    # Fetches active asteroid assets from NASA fetcher and applies them to the grid
    def reload_asteroids(self):
        self.asteroids_dataset = self.fetcher.fetch_asteroids()
        self.sync_obstacles_to_grid()

    # Populates the A* grid obstacles from the active stage datasets.
    def sync_obstacles_to_grid(self):
        self.grid_model.reset_grid()
        self.active_scanned_object = None

        if self.current_stage == 1:
            # Stage 1: Load Asteroids (Planets are left passable as stations!)
            for ast in self.asteroids_dataset:
                self.grid_model.set_obstacle(ast["x"], ast["y"], is_obstacle=True, celestial_obj=ast)
        else:
            # Stage 2: Load Stars, Galaxies, Nebulae
            for obj in self.deep_space_dataset:
                self.grid_model.set_obstacle(obj["x"], obj["y"], is_obstacle=True, celestial_obj=obj)

        # Apply hazard buffer costs surrounding obstacles
        self.grid_model.apply_hazard_margins(margin_radius=1, cost_increment=5.0)


    # Constructs layout buttons on the sidebar panel dynamically based on sidebar dimensions
    def _build_ui_buttons(self):
        sb_x = self.sidebar_x
        sb_w = self.sidebar_width

        # Heights of button rows
        r1_y = 90
        r2_y = 125
        r3_y = 160
        r4_y = 195  # Mouse Click Mode and Heuristic Toggle row

        # Two-column layout in the sidebar
        col_w = (sb_w - 40) // 2
        col1_x = sb_x + 15
        col2_x = sb_x + 15 + col_w + 10

        self.buttons = [
            Button((col1_x, r1_y, col_w, 30), "STAGE 01: NEO BELT", "stage_1", COLOR_ACCENT_CYAN, toggle_state=(self.current_stage == 1)),
            Button((col2_x, r1_y, col_w, 30), "STAGE 02: DEEP SPACE", "stage_2", COLOR_ACCENT_CYAN, toggle_state=(self.current_stage == 2)),

            Button((col1_x, r2_y, col_w, 30), "CALCULATE PATH", "calc_path", COLOR_ACCENT_GREEN),
            Button((col2_x, r2_y, col_w, 30), "AUTOPILOT: LAUNCH", "launch", COLOR_ACCENT_CYAN),

            Button((col1_x, r3_y, col_w, 30), "REFETCH DATA", "refresh", COLOR_ACCENT_AMBER),
            Button((col2_x, r3_y, col_w, 30), "TOGGLE SEARCH TREE", "toggle_tree", COLOR_ACCENT_CYAN, toggle_state=self.show_search_tree),

            Button((col1_x, r4_y, col_w, 30), f"MOUSE: SET {self.mouse_mode.upper()}", "click_mode", COLOR_ACCENT_GREEN if self.mouse_mode == "start" else COLOR_ACCENT_MAGENTA),
            Button((col2_x, r4_y, col_w, 30), f"HEURISTIC: {self.heuristic_mode.upper()}", "heuristic", COLOR_ACCENT_CYAN)
        ]

        # Station selection arrows placed dynamically (Row 5 at y = 235, Row 6 at y = 265)
        self.buttons.append(Button((sb_x + 15, 235, 30, 25), "<", "start_prev", COLOR_ACCENT_CYAN))
        self.buttons.append(Button((sb_x + sb_w - 45, 235, 30, 25), ">", "start_next", COLOR_ACCENT_CYAN))

        self.buttons.append(Button((sb_x + 15, 265, 30, 25), "<", "target_prev", COLOR_ACCENT_CYAN))
        self.buttons.append(Button((sb_x + sb_w - 45, 265, 30, 25), ">", "target_next", COLOR_ACCENT_CYAN))

    # Returns the name of the celestial body at a coordinate, or formatted coordinate string if custom
    def _get_body_name_at_pos(self, pos):
        if self.current_stage == 1:
            for p in self.stage_1_planets:
                if (p["x"], p["y"]) == pos:
                    return p["name"]
        else:
            for p in self.deep_space_dataset:
                if (p["x"], p["y"]) == pos:
                    return p["name"]
        return f"Sector {pos[0]},{pos[1]}"

    # Returns a list of dictionaries with name, x, y coordinates for selection in the active stage
    def _get_selectable_bodies(self):
        if self.current_stage == 1:
            return [{"name": p["name"], "pos": (p["x"], p["y"])} for p in self.stage_1_planets]
        else:
            return [{"name": p["name"], "pos": (p["x"], p["y"])} for p in self.deep_space_dataset]

    # Runs the A* pathfinding search between start_node and end_node
    def calculate_path(self):
        self.active_path, self.open_list_vis, self.closed_list_vis = self.grid_model.search(
            self.start_node, self.end_node, heuristic_mode=self.heuristic_mode
        )
        self.reset_ship_animation()

    # Resets the spaceship visual animation back to start coordinates
    def reset_ship_animation(self):
        self.is_animating = False
        self.anim_index = 0
        self.ship_x = float(self.start_node[0])
        self.ship_y = float(self.start_node[1])
        self.fuel_level = 100.0

    # Begins autopilot movement sequence
    def trigger_autopilot(self):
        if self.active_path and len(self.active_path) > 1:
            self.is_animating = True
            self.anim_index = 0
            self.ship_x = float(self.active_path[0][0])
            self.ship_y = float(self.active_path[0][1])
            self.fuel_level = 100.0
