# Void-Navigator

**An Interactive Space Pathfinding Simulation using A* Search**

---

| | |
|---|---|
| **Course** | CSE 3812 (E): Artificial Intelligence Laboratory |
| **Section** | E |
| **Instructor** | Mr. A.H.M. Osama Haque \| Lecturer, Dept. of CSE |
| **Institute** | United International University |
| **Technology** | Python, Pygame, NASA NEO API |

---

## Team Members

| ID | Name |
|---|---|
| **0112410222** | **Md. Ashikuzzaman Rahad** |
| 0112410202 | Seam Islam Omi |
| 0112330067 | Md. Siaum Ahmed |

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Folder Structure](#folder-structure)
3. [Module Descriptions](#module-descriptions)
4. [Tech Stack & APIs](#tech-stack--apis)
5. [Key Functionalities](#key-functionalities)
6. [A\* Search Algorithm: Theory & Implementation](#a-search-algorithm-theory--implementation)
7. [Installation & Setup](#installation--setup)
8. [How to Run](#how-to-run)
9. [Controls & Usage](#controls--usage)

---

## Project Overview

**Void-Navigator** is an interactive space-pathfinding simulation built for the Artificial Intelligence Laboratory course. The application allows users to chart optimal routes through asteroid fields and deep-space celestial bodies using the **A\* (A-star) search algorithm**.

Users can fetch real asteroid data from the **NASA Near-Earth Object (NEO) REST API**, visualize a 50×50 radar grid, toggle between different heuristic functions, and launch an animated autopilot spaceship that traverses the computed optimal path. The simulation features procedurally rendered planets, asteroids, stars, galaxies, and nebulae, all presented through a sci-fi-themed heads-up display (HUD).

The project demonstrates a complete pipeline: real-world API data acquisition, spatial reasoning via heuristic search, procedural graphics rendering, and interactive user interface design in a single cohesive application.

---

## Folder Structure

```
Void-Navigator/
│
├── .env                        # NASA API key (environment variable)
├── .gitignore                  # Git exclusion rules
├── README.md                   # Project documentation
├── main.py                     # Application entry point: Pygame UI, rendering, event loop
├── nasa_api.py                 # NASA NEO REST API client & offline celestial catalogs
├── navigator.py                # A* pathfinding engine: Node, AStarGrid, search algorithm
└── __pycache__/                # Python bytecode cache (auto-generated)
```

---

## Module Descriptions

### `main.py` — Application Controller & Renderer (1228 lines)

The central module that initializes and orchestrates the entire application. It contains:

- **`VoidNavigatorApp`** — Main application class managing the Pygame window, event handling, frame updates, and all rendering. Initializes the A* engine, NASA data fetcher, and particle engine.
- **`CosmicObjectRenderer`** — Static methods for procedurally rendering planets (glow, continents, crescent shadows), asteroids (jagged polygons, hazard glow), stars (spectral-class coloring, pulsing), galaxies (rotating spiral particles), and nebulae (soft drifting gas clouds).
- **`ParticleEngine`** — Manages thruster exhaust particles emitted behind the spaceship during autopilot, with position, velocity, life decay, and color fade.
- **`Button`** — Reusable sci-fi-styled UI button with hover detection, toggle states, and corner tick decorations.

### `nasa_api.py` — Data Acquisition Layer (208 lines)

Provides the `NASADataFetcher` class responsible for:

- Querying the **NASA NEO REST API** (`/neo/rest/v1/feed`) for real asteroid data within a user-specified date range.
- Parsing API responses into structured data (name, diameter, velocity, miss distance, hazard status).
- Deterministic grid-coordinate generation using MD5 hashing of asteroid IDs.
- **Offline fallback**: 16 hard-coded real asteroids (Apophis, Bennu, Ryugu, Eros, etc.) used when the API is unreachable.
- **Deep-space catalog**: 18 pre-defined celestial objects (Sirius, Betelgeuse, Orion Nebula, Andromeda Galaxy, etc.) with spectral classes, magnitudes, and distances.

### `navigator.py` — A* Search Engine (220 lines)

The core algorithmic module implementing the A* pathfinding system:

- **`Node`** — Represents a single grid cell with `g` (cost from start), `h` (heuristic to goal), `f` (total = g + h), `parent` (for path reconstruction), `is_obstacle`, `hazard_weight`, and a reference to an attached celestial object.
- **`AStarGrid`** — Manages a 2D grid (50×50 = 2,500 nodes), provides obstacle placement, hazard margin computation, neighbor enumeration (8-directional), heuristic evaluation (Octile / Euclidean / Manhattan), and the A* search routine using a priority queue (`heapq`).

---

## Tech Stack & APIs

| Category | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.12+ | Core programming language |
| **Graphics Engine** | Pygame 2.x | Windowing, rendering, input handling, clock |
| **HTTP Client** | `requests` | Consuming the NASA REST API |
| **Environment** | `python-dotenv` | Loading the NASA API key from `.env` |
| **Priority Queue** | `heapq` (stdlib) | Efficient open-set management in A* |
| **Mathematics** | `math` (stdlib) | Heuristics, trigonometry for rendering |
| **Hashing** | `hashlib.md5` (stdlib) | Deterministic coordinate generation |
| **Datetime** | `datetime` (stdlib) | Date handling for API queries |
| **Randomization** | `random` (stdlib) | Procedural generation, particle effects |

### External API

- **NASA Near-Earth Object Web Service (NEO WS)**
  - Endpoint: `https://api.nasa.gov/neo/rest/v1/feed`
  - Provides real-time data on near-Earth asteroids (names, diameters, velocities, miss distances, hazardous classifications) for a given date range.
  - Requires a free API key stored in the `.env` file.

---

## Key Functionalities

### Celestial Data & API Integration

- Fetches real asteroid data from the NASA NEO API using user-specified date fields.
- Seamless offline fallback to a curated catalog of 16 famous asteroids with realistic physical parameters.
- Pre-defined deep-space catalog of 18 objects (stars, nebulae, galaxies) with spectral classifications, distances, and magnitudes.

### Two Distinct Stages

1. **NEO Belt (Stage 1)** — Navigate through real/fictional asteroids with planets (Earth, Mars, Mercury, Venus, Jupiter, Saturn) as waypoints.
2. **Deep Space (Stage 2)** — Navigate through stars, nebulae, and galaxies as obstacles.

### A* Pathfinding Engine

- 8-directional movement on a 50×50 grid with orthogonal (cost 1.0) and diagonal (cost ≈1.414) steps.
- Three user-selectable heuristic modes: **Octile** (default, optimal for 8-way grids), **Euclidean**, **Manhattan**.
- Hazard margin system that applies distance-decayed cost penalties around obstacles, discouraging paths that graze too close.
- Search-tree visualization: toggleable overlay showing the open set (nodes under consideration, green) and closed set (already evaluated nodes, red).

### Interactive Controls

- Mouse-based grid interaction: set start point, target point, or scan obstacle data.
- Right-click shortcut to set the target node.
- Cycle-buttons (`<` / `>`) to quickly select predefined celestial start/target positions.
- Autopilot launch command with real-time ship traversal animation.

### Visual & Simulation Systems

- Twinkling starfield background (200 stars with randomized properties).
- Animated radar-sweep line rotating over the grid.
- Delta-wing spaceship model that orients toward its heading direction with thruster exhaust particle effects.
- Hazard-adaptive autopilot speed: the ship decelerates in high-risk regions.
- Fuel simulation with a percentage bar displayed in the HUD.
- Procedural rendering of celestial bodies:
  - **Planets** — atmospheric glow, surface continents (Earth-style), storm bands, crescent shadow overlay.
  - **Asteroids** — irregular jagged polygons with red hazard glow for dangerous objects.
  - **Stars** — spectral-type coloring (O/B/A/F/G/K/M), pulsing brightness.
  - **Galaxies** — animated 2-arm spiral patterns from particle arrays.
  - **Nebulae** — overlapping semi-transparent drifting gas clouds.
- Pulsing green/magenta rings at start and target positions.

### Sensor & Telemetry HUD

- Proximity scanner detecting the nearest celestial object within 6 grid cells of the ship.
- Rotating 3D wireframe hologram preview of the scanned object in the radar panel.
- HUD telemetry displaying coordinates, fuel percentage, path node count, and accumulated path cost.
- Status indicators: "SYSTEM FLIGHT READY", "AUTOPILOT TRANSIT ENGAGED", "GRAVITATIONAL WELL DETECTED".
- Amber hazard-alarm border when the ship enters a danger zone.

### UI & Responsiveness

- Dynamic window resizing with minimum dimensions (800 × 550).
- Sci-fi themed button system with hover glow, toggle highlights, and corner decorations.
- 60 FPS locked frame rate for smooth animation.

---

## A\* Search Algorithm: Theory & Implementation

### Algorithm Overview

The A* (A-star) algorithm is a best-first graph traversal and pathfinding algorithm that guarantees finding the shortest path from a start node to a goal node, provided a consistent (monotone) heuristic is used. It combines the strengths of Dijkstra's algorithm (which prioritizes nodes near the start) and Greedy Best-First Search (which prioritizes nodes near the goal).

A* evaluates nodes using the evaluation function:

```
f(n) = g(n) + h(n)
```

Where:

- **`f(n)`** — Total estimated cost of the path through node `n`.
- **`g(n)`** — The exact cost of the path from the start node to node `n`.
- **`h(n)`** — A heuristic estimate of the cost from node `n` to the goal.

The algorithm maintains two data structures:

- **Open Set** — Nodes discovered but not yet evaluated (priority queue ordered by `f`).
- **Closed Set** — Nodes already fully evaluated.

### Implementation in `navigator.py`

#### Node Representation (`Node` class)

Each cell on the grid is a `Node` object storing:

- `g` — Accumulated path cost from start (initialized to `inf`).
- `h` — Heuristic estimate to goal.
- `f` — Sum of `g` and `h`.
- `parent` — Pointer to the predecessor node for path reconstruction.
- `is_obstacle` — Boolean flag marking impassable cells.
- `hazard_weight` — Additional traversal cost near obstacles (safety margin).

Tie-breaking is implemented by comparing `f` values; when equal, the node with a lower `h` (closer to the goal) is expanded first, biasing the search toward the goal direction.

#### Grid Management (`AStarGrid` class)

A 50 × 50 2D grid is constructed, yielding 2,500 navigable cells. Obstacles (asteroids, stars, etc.) are marked as impassable, and celestial object references are attached for rendering.

#### Hazard Margin System

After placing obstacles, `apply_hazard_margins()` iterates over every obstacle and applies a distance-decayed cost penalty to neighboring cells:

```
hazard_weight = cost_increment / distance  (default cost_increment = 5.0)
```

Adjacent cells (Chebyshev distance 1) receive a weight of 5.0, diagonal neighbors receive approximately 3.54, and weights accumulate if a cell lies near multiple obstacles. This creates a smooth cost gradient that steers the path away from hazards without entirely blocking passage.

#### Neighbor Generation

8-directional (king's move) connectivity is used:

- **Orthogonal neighbors** (up, down, left, right): step cost = **1.0**
- **Diagonal neighbors**: step cost = **√2 ≈ 1.414**

Obstacle cells are excluded from the neighbor list.

#### Heuristic Functions

Three heuristic modes are available, each modelling a different distance metric:

1. **Octile Distance** (default)

   ```
   h(n) = D × (dx + dy) + (D₂ - 2D) × min(dx, dy)
   ```

   Where `D = 1.0` (orthogonal cost) and `D₂ = 1.414` (diagonal cost). This is the exact shortest-path distance on an 8-connected grid and is both **admissible** (never overestimates) and **consistent** (satisfies the triangle inequality), guaranteeing optimal solutions with the fewest node expansions.

2. **Euclidean Distance**

   ```
   h(n) = √(dx² + dy²)
   ```

   Straight-line distance. Admissible but may underestimate the actual path cost, leading to more node expansions.

3. **Manhattan Distance**

   ```
   h(n) = dx + dy
   ```

   Appropriate for 4-directional movement only. Underestimates on 8-connected grids, causing more exploration but remaining admissible.

#### The A\* Search Procedure

The `search(start_pos, end_pos, heuristic_mode)` method implements the canonical A* algorithm:

1. **Forcing passability** — The start and end nodes are marked passable even if they coincide with an obstacle, preventing deadlock.

2. **Initialization** — All nodes are reset (`g = inf`, `f = inf`, `parent = None`). The start node is set with `g = 0`, its heuristic `h` is computed, and `f = g + h`. The start is pushed onto the priority queue (`open_queue`) and added to the `open_set`.

3. **Main loop** — While the priority queue is not empty:
   - Pop the node with the lowest `f` value from the heap.
   - If it is already in the closed set, skip it (handles stale heap entries).
   - Move the node from the open set to the closed set.
   - **Goal test**: If the current node is the goal, reconstruct the path by following `parent` pointers from the goal back to the start, reverse the list, and return the path along with the open and closed sets for visualization.
   - **Neighbor expansion**: For each valid, unprocessed neighbor:
     ```
     tentative_g = current.g + step_cost + neighbor.hazard_weight
     ```
     If `tentative_g < neighbor.g`, update the neighbor's `parent`, `g`, `h`, and `f`. If the neighbor is not in the open set, push it onto the heap.

4. **Termination** — If the queue empties without reaching the goal, return `None` (no path exists).

#### Path Reconstruction

When the goal is reached, the path is reconstructed by walking the `parent` chain:

```python
path = []
temp = current
while temp:
    path.append(temp.pos)
    temp = temp.parent
path.reverse()          # Now start → goal
```

#### Visualizing the Search Tree

The open and closed sets are returned by the search method and rendered as translucent colored overlays:

- **Open set** → green overlay (nodes awaiting evaluation).
- **Closed set** → red overlay (nodes already evaluated).

This allows users to observe the algorithm's exploration pattern in real time.

### Optimality and Completeness

Because all three heuristic options are **admissible** (they never overestimate the true path cost), the implementation is guaranteed to find the **optimal (shortest) path** when one exists. The algorithm is also **complete**: it will always find a path if one exists and will correctly report failure otherwise.

---

## Installation & Setup

### Prerequisites

- Python 3.12 or later
- pip (Python package manager)

### Dependencies

Install the required packages:

```bash
pip install pygame requests python-dotenv
```

### NASA API Key (Optional)

1. Obtain a free API key from [https://api.nasa.gov/](https://api.nasa.gov/).
2. Create a `.env` file in the project root (a sample is already provided):

```env
NASA_API_KEY=your_api_key_here
```

The application works without a valid key by falling back to an offline asteroid catalog.

---

## How to Run

```bash
python main.py
```

The application launches in a 1020 × 680 resizable window. The main loop runs at 60 FPS with the sequence: **Handle Events → Update → Draw**.

---

## Controls & Usage

| Action | Input |
|---|---|
| Set start node | Left-click on grid (in "Start" mouse mode) |
| Set target node | Left-click on grid (in "Target" mouse mode) / Right-click anywhere |
| Scan obstacle | Left-click on grid (in "Scan" mouse mode) |
| Switch mouse mode | Click the "Mouse Mode" sidebar button |
| Switch stage | Click "NEO Belt" or "Deep Space" button |
| Toggle heuristic | Click "Heuristic" button (cycles: Octile → Euclidean → Manhattan) |
| Calculate path | Click "Calculate Path" button |
| Launch autopilot | Click "Autopilot Launch" button |
| Toggle search tree | Click "Toggle Search Tree" button |
| Refetch NASA data | Click "Refetch Data" button |
| Edit date range | Select date field and type (start/end date for API queries) |
| Cycle start/target | Click `<` / `>` arrow buttons |
| Quit | Close window or Ctrl+C |

---

## Acknowledgements

- **NASA JPL** for the Near-Earth Object Web Service API.
- **Pygame Community** for the graphics and game-development framework.
- **United International University** for providing the academic environment that enabled this project.

---

*Void-Navigator — CSE 3812 (E): Artificial Intelligence Laboratory*
