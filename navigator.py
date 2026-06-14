import heapq
import math

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf')  # Cost from start node to this node
        self.h = 0.0           # Heuristic cost from this node to goal
        self.f = float('inf')  # Total cost: f = g + h
        self.parent = None     # Parent node in the search tree
        self.is_obstacle = False
        self.hazard_weight = 0.0  # Extra cost to discourage pathfinder from scraping close to obstacles
        self.celestial_obj = None  # Reference to the actual celestial object if it is an obstacle

    def __lt__(self, other):
        # Tie-breaker logic for heapq: lower f is prioritized. If f is equal, prioritize lower h (closer to goal)
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    @property
    def pos(self):
        return (self.x, self.y)


class AStarGrid:
    """
    Manages the 2D grid and execution of the A* pathfinding algorithm.
    """
    def __init__(self, size=40):
        self.size = size
        self.grid = {}
        self.reset_grid()

    def reset_grid(self):
        """Re-initializes all grid nodes to a clean state."""
        self.grid = {}
        for x in range(self.size):
            for y in range(self.size):
                self.grid[(x, y)] = Node(x, y)

    def set_obstacle(self, x, y, is_obstacle=True, celestial_obj=None):
        """Sets a node as passable or impassable, associating a celestial object if applicable."""
        if (x, y) in self.grid:
            node = self.grid[(x, y)]
            node.is_obstacle = is_obstacle
            node.celestial_obj = celestial_obj

    def get_node(self, x, y):
        """Returns the node at the specified coordinate."""
        return self.grid.get((x, y))

    def apply_hazard_margins(self, margin_radius=1, cost_increment=5.0):
        """
        Scans the grid and adds a hazard weight to cells surrounding obstacles.
        This represents gravity wells or asteroid debris fields, pushing the A* pathfinder
        to steer clear of obstacles with a safety buffer.
        """
        # First reset all hazard weights
        for node in self.grid.values():
            node.hazard_weight = 0.0

        # Apply hazard costs around all active obstacles
        for (x, y), node in self.grid.items():
            if node.is_obstacle:
                # Traverse neighbors within the radius
                for dx in range(-margin_radius, margin_radius + 1):
                    for dy in range(-margin_radius, margin_radius + 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        neighbor = self.get_node(nx, ny)
                        if neighbor and not neighbor.is_obstacle:
                            # Distance-based decay of hazard cost (higher cost closer to the object)
                            dist = math.sqrt(dx*dx + dy*dy)
                            weight = (cost_increment / dist)
                            # Accumulate weights in case a node is near multiple obstacles
                            neighbor.hazard_weight += round(weight, 2)

    def get_neighbors(self, node):
        """
        Returns all valid, passable neighboring nodes for an 8-way movement system.
        """
        neighbors = []
        # Movement offsets (x, y, movement_cost)
        # Standard step cost is 1.0, diagonal step cost is sqrt(2) ≈ 1.414
        directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),   # Orthogonal
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414) # Diagonal
        ]

        for dx, dy, step_cost in directions:
            nx, ny = node.x + dx, node.y + dy
            neighbor = self.get_node(nx, ny)
            if neighbor and not neighbor.is_obstacle:
                neighbors.append((neighbor, step_cost))
        return neighbors

    def _heuristic(self, node, goal, mode="octile"):
        """
        Heuristic cost estimation.
        Using Octile distance which is mathematically accurate for 8-way movement.
        """
        dx = abs(node.x - goal.x)
        dy = abs(node.y - goal.y)

        if mode == "octile":
            # Diagonal steps cost 1.414, orthogonal cost 1.0
            return (dx + dy) + (1.414 - 2.0) * min(dx, dy)
        elif mode == "euclidean":
            return math.sqrt(dx * dx + dy * dy)
        else:
            # Manhattan distance (best for 4-way, but usable here)
            return dx + dy

    def search(self, start_pos, end_pos, heuristic_mode="octile"):
        """
        Executes the A* pathfinding algorithm.
        Returns:
            path: List of (x, y) coordinates representing the shortest path, or None if unreachable.
            open_nodes: Set of node coordinates visited/in search queue (for visualizer overlays).
            closed_nodes: Set of completed node coordinates (for visualizer overlays).
        """
        start_node = self.get_node(*start_pos)
        end_node = self.get_node(*end_pos)

        if not start_node or not end_node:
            return None, set(), set()

        # If start or end is inside an obstacle, make it temporarily passable to avoid search lockups
        start_node.is_obstacle = False
        end_node.is_obstacle = False

        # Reset search values on all nodes before running
        for node in self.grid.values():
            node.g = float('inf')
            node.f = float('inf')
            node.parent = None

        start_node.g = 0.0
        start_node.h = self._heuristic(start_node, end_node, heuristic_mode)
        start_node.f = start_node.g + start_node.h

        # Priority queue stores (f_value, unique_counter, node_object) to avoid node sorting collisions
        open_queue = []
        counter = 0
        heapq.heappush(open_queue, (start_node.f, counter, start_node))

        # Set trackers for Pygame search visualizer
        open_set = {start_node.pos}
        closed_set = set()

        while open_queue:
            current_f, _, current = heapq.heappop(open_queue)

            if current.pos in closed_set:
                continue

            # Remove from open list tracking, add to closed
            if current.pos in open_set:
                open_set.remove(current.pos)
            closed_set.add(current.pos)

            # Goal reached: reconstruct and return path
            if current.pos == end_node.pos:
                path = []
                temp = current
                while temp:
                    path.append(temp.pos)
                    temp = temp.parent
                path.reverse()
                return path, open_set, closed_set

            # Process neighbors
            for neighbor, step_cost in self.get_neighbors(current):
                if neighbor.pos in closed_set:
                    continue

                # Path cost = current cost + step length (1.0 or 1.414) + neighbor's hazard penalty
                tentative_g = current.g + step_cost + neighbor.hazard_weight

                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self._heuristic(neighbor, end_node, heuristic_mode)
                    neighbor.f = neighbor.g + neighbor.h

                    if neighbor.pos not in open_set:
                        counter += 1
                        heapq.heappush(open_queue, (neighbor.f, counter, neighbor))
                        open_set.add(neighbor.pos)

        # Path not found
        return None, open_set, closed_set

# Simple verification block
if __name__ == "__main__":
    grid = AStarGrid(size=10)
    # Add a simple barrier
    grid.set_obstacle(4, 3, True)
    grid.set_obstacle(4, 4, True)
    grid.set_obstacle(4, 5, True)

    # Calculate hazards
    grid.apply_hazard_margins(margin_radius=1, cost_increment=3.0)

    # Run pathfinding
    start = (1, 4)
    end = (8, 4)
    path, opens, closeds = grid.search(start, end)

    print("Test path:", path)
    print("Closed nodes:", len(closeds))
    if path:
        print("Success! Path navigated around barrier.")
        # Check if it avoided the adjacent hazard zone if possible
        for x, y in path:
            node = grid.get_node(x, y)
            print(f"Node {x},{y} has hazard weight: {node.hazard_weight}")
