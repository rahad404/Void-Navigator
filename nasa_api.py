import os
import requests
import datetime
import random
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Default NASA API Key (rate-limited, can be overridden by environment variable)
# NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
api_key = os.getenv("NASA_API_KEY")
if not api_key:
    raise ValueError("NASA_API_KEY environment variable not set")

class NASADataFetcher:
    def __init__(self, grid_size=50):
        self.grid_size = grid_size
        self.offline_asteroids = self._generate_offline_asteroids()
        self.deep_space_catalog = self._generate_deep_space_catalog()

    def fetch_asteroids(self, start_date=None, end_date=None):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            start_date = today
        if end_date is None:
            end_date = today
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={api_key}"

        try:
            # Short timeout to avoid freezing the Pygame app
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Aggregate asteroids from all dates in the response
                asteroids_raw = []
                for date_key in data.get("near_earth_objects", {}):
                    asteroids_raw.extend(data["near_earth_objects"][date_key])
                return self._parse_nasa_asteroids(asteroids_raw)
            else:
                print(f"NASA API returned status code {response.status_code}. Using high-fidelity offline asteroid catalog.")
                return self.offline_asteroids
        except Exception as e:
            print(f"Network error while connecting to NASA API: {e}. Using high-fidelity offline asteroid catalog.")
            return self.offline_asteroids

    def _parse_nasa_asteroids(self, asteroids_raw):
        # Parses raw NASA API data and assigns coordinates on the grid dynamically.
        parsed = []
        for index, ast in enumerate(asteroids_raw):
            ast_id = ast.get("id", str(index))
            name = ast.get("name", "Unknown Asteroid")

            # Diameters in kilometers
            diam_dict = ast.get("estimated_diameter", {}).get("kilometers", {})
            min_diam = diam_dict.get("estimated_diameter_min", 0.1)
            max_diam = diam_dict.get("estimated_diameter_max", 0.5)
            diameter = round((min_diam + max_diam) / 2.0, 3)

            # Speed and miss distance
            approach = ast.get("close_approach_data", [{}])[0]
            velocity = round(float(approach.get("relative_velocity", {}).get("kilometers_per_hour", 0)), 1)
            miss_dist = round(float(approach.get("miss_distance", {}).get("kilometers", 0)), 1)
            is_hazardous = ast.get("is_potentially_hazardous_asteroid", False)

            # Map deterministically to grid using a hash of the asteroid ID
            x, y = self._generate_coordinates_from_hash(ast_id, avoid_regions=[(5, 5), (self.grid_size - 6, self.grid_size - 6)])

            parsed.append({
                "id": ast_id,
                "name": name,
                "type": "Asteroid",
                "x": x,
                "y": y,
                "diameter_km": diameter,
                "velocity_kph": velocity,
                "miss_distance_km": miss_dist,
                "is_hazardous": is_hazardous,
                "description": f"A Near-Earth asteroid cataloged by NASA. Estimated diameter is {diameter} km, moving at {velocity:,} km/h."
            })
        return parsed

    def _generate_coordinates_from_hash(self, unique_id, avoid_regions, margin=3):
        """
        Generates deterministic coordinates (x, y) on the grid using a hash of the ID.
        Ensures the coordinates don't fall too close to the specified avoid_regions (e.g., Earth and Mars positions).
        """
        h = hashlib.md5(unique_id.encode('utf-8')).hexdigest()

        # Parse hash to coordinates
        x_seed = int(h[:8], 16)
        y_seed = int(h[8:16], 16)

        # Grid range, leaving a margin at the edges
        min_val = margin
        max_val = self.grid_size - margin - 1

        x = min_val + (x_seed % (max_val - min_val + 1))
        y = min_val + (y_seed % (max_val - min_val + 1))

        # If coordinates overlap with any start/end region, shift them
        for rx, ry in avoid_regions:
            if abs(x - rx) <= 3 and abs(y - ry) <= 3:
                x = (x + 7) % (max_val - min_val + 1) + min_val
                y = (y + 11) % (max_val - min_val + 1) + min_val

        return x, y

    def _generate_offline_asteroids(self):
        """
        Generates a robust fallback list of detailed near-Earth asteroids if offline or rate-limited.
        """
        fallback_data = [
            ("99942 Apophis", 0.370, 110000, 31000, True),
            ("101955 Bennu", 0.490, 101000, 203000, True),
            ("162173 Ryugu", 0.900, 85000, 950000, False),
            ("433 Eros", 16.8, 88000, 22000000, False),
            ("25143 Itokawa", 0.330, 92000, 1800000, False),
            ("4179 Toutatis", 5.4, 111000, 7000000, True),
            ("3200 Phaethon", 5.8, 126000, 10000000, True),
            ("1862 Apollo", 1.5, 78000, 5000000, True),
            ("6489 Golevka", 0.530, 68000, 15000000, False),
            ("1981 Midas", 3.4, 94000, 12000000, False),
            ("1566 Icarus", 1.4, 104000, 8000000, True),
            ("2004 MN4", 0.320, 109000, 38000, True),
            ("Ceres", 939.4, 64000, 260000000, False),
            ("4 Vesta", 525.4, 70000, 220000000, False),
            ("2 Pallas", 512.0, 68000, 270000000, False),
            ("10 Hygiea", 434.0, 60000, 310000000, False)
        ]

        parsed = []
        for index, (name, diameter, velocity, miss_dist, is_hazardous) in enumerate(fallback_data):
            x, y = self._generate_coordinates_from_hash(name, avoid_regions=[(5, 5), (self.grid_size - 6, self.grid_size - 6)])
            parsed.append({
                "id": f"offline_{index}",
                "name": name,
                "type": "Asteroid",
                "x": x,
                "y": y,
                "diameter_km": diameter,
                "velocity_kph": velocity,
                "miss_distance_km": miss_dist,
                "is_hazardous": is_hazardous,
                "description": f"Real asteroid tracked by NASA. Diameter: {diameter} km. Speed: {velocity:,} km/h."
            })
        return parsed

    def _generate_deep_space_catalog(self):
        """
        Returns a beautifully detailed catalog of major visible stars, galaxies, and nebulae.
        """
        # Formatted details of famous cosmic bodies. Coordinates are scaled mathematically.
        raw_catalog = [
            # Stars (Pre-discretized x,y values to make pathfinding interesting and challenging)
            {"name": "Sirius", "type": "Star", "x": 10, "y": 8, "spectral": "A1V", "distance_ly": 8.6, "magnitude": -1.46, "desc": "The brightest star in the night sky. Also known as the Dog Star."},
            {"name": "Betelgeuse", "type": "Star", "x": 28, "y": 12, "spectral": "M1-M2Ia", "distance_ly": 640, "magnitude": 0.50, "desc": "A massive red supergiant star in the constellation Orion, nearing the end of its life."},
            {"name": "Rigel", "type": "Star", "x": 32, "y": 28, "spectral": "B8Ia", "distance_ly": 860, "magnitude": 0.13, "desc": "A luminous blue supergiant star in Orion. One of the brightest stars in the galaxy."},
            {"name": "Vega", "type": "Star", "x": 15, "y": 30, "spectral": "A0V", "distance_ly": 25, "magnitude": 0.03, "desc": "A bright star in the constellation Lyra. Used historically as a baseline for stellar magnitude."},
            {"name": "Arcturus", "type": "Star", "x": 8, "y": 22, "spectral": "K1.5III", "distance_ly": 36.7, "magnitude": -0.05, "desc": "A highly luminous red giant star, the brightest in the northern celestial hemisphere."},
            {"name": "Polaris", "type": "Star", "x": 20, "y": 35, "spectral": "F7Ib", "distance_ly": 433, "magnitude": 1.97, "desc": "The North Star. It is very close to the north celestial pole, useful for navigation."},
            {"name": "Alpha Centauri", "type": "Star", "x": 5, "y": 15, "spectral": "G2V / K1V", "distance_ly": 4.37, "magnitude": -0.27, "desc": "The closest star system to our Solar System, consisting of three stars."},
            {"name": "Aldebaran", "type": "Star", "x": 22, "y": 25, "spectral": "K5III", "distance_ly": 65, "magnitude": 0.85, "desc": "A red giant star located in the Taurus constellation, representing the Eye of the Bull."},
            {"name": "Antares", "type": "Star", "x": 12, "y": 18, "spectral": "M1.5Iab", "distance_ly": 550, "magnitude": 1.06, "desc": "A huge red supergiant at the heart of Scorpius, glowing with distinct reddish light."},

            # Nebulae (Act as larger gas clouds - larger obstacle/gravitational impact)
            {"name": "Orion Nebula", "type": "Nebula", "x": 30, "y": 15, "spectral": "H II Region", "distance_ly": 1344, "magnitude": 4.0, "desc": "A massive stellar nursery. It is one of the brightest nebulae, visible to the naked eye."},
            {"name": "Crab Nebula", "type": "Nebula", "x": 25, "y": 26, "spectral": "Supernova Remnant", "distance_ly": 6500, "magnitude": 8.4, "desc": "The expanding remnant of a massive star explosion observed by astronomers in the year 1054."},
            {"name": "Ring Nebula", "type": "Nebula", "x": 16, "y": 28, "spectral": "Planetary Nebula", "distance_ly": 2300, "magnitude": 8.8, "desc": "A glowing shell of ionized gas expelled into space by a dying red giant star."},
            {"name": "Eagle Nebula", "type": "Nebula", "x": 18, "y": 10, "spectral": "Emission Nebula", "distance_ly": 7000, "magnitude": 6.0, "desc": "Home to the famous 'Pillars of Creation', a majestic star-forming region of gas and dust."},
            {"name": "Carina Nebula", "type": "Nebula", "x": 6, "y": 26, "spectral": "Diffuse Nebula", "distance_ly": 8500, "magnitude": 1.0, "desc": "One of the largest diffuse nebulae in our skies, containing extremely massive stars like Eta Carinae."},

            # Galaxies (Massive coordinates, complex gravitational field)
            {"name": "Andromeda Galaxy", "type": "Galaxy", "x": 35, "y": 6, "spectral": "Spiral (Sb)", "distance_ly": 2537000, "magnitude": 3.44, "desc": "The closest major spiral galaxy to the Milky Way, on a collision course with us in 4.5 billion years."},
            {"name": "Triangulum Galaxy", "type": "Galaxy", "x": 36, "y": 20, "spectral": "Spiral (Sc)", "distance_ly": 2730000, "magnitude": 5.72, "desc": "The third-largest member of the Local Group of galaxies, after Andromeda and the Milky Way."},
            {"name": "Large Magellanic Cloud", "type": "Galaxy", "x": 3, "y": 32, "spectral": "Satellite / Irregular", "distance_ly": 158200, "magnitude": 0.9, "desc": "A satellite galaxy of the Milky Way, visible as a faint cosmic cloud from the southern hemisphere."},
            {"name": "Sombrero Galaxy", "type": "Galaxy", "x": 14, "y": 3, "spectral": "Spiral (Sa)", "distance_ly": 29000000, "magnitude": 8.0, "desc": "A stunning spiral galaxy with an unusually large central bulge and a prominent dark dust lane."}
        ]

        catalog = []
        for obj in raw_catalog:
            # Format uniform database fields
            catalog.append({
                "id": f"deep_{obj['name'].lower().replace(' ', '_')}",
                "name": obj["name"],
                "type": obj["type"],
                "x": obj["x"],
                "y": obj["y"],
                "spectral_class": obj.get("spectral", "N/A"),
                "distance_ly": obj.get("distance_ly", 0.0),
                "magnitude": obj.get("magnitude", 0.0),
                "description": obj["desc"]
            })
        return catalog

# Simple test execution to confirm it works
if __name__ == "__main__":
    fetcher = NASADataFetcher(grid_size=40)
    print("Testing NASA Asteroid Fetch...")
    asteroids = fetcher.fetch_asteroids()
    print(f"Successfully fetched/generated {len(asteroids)} asteroids.")
    if asteroids:
        print("First asteroid data:", asteroids[0])

    print("\nTesting Deep Space Catalog...")
    catalog = fetcher.deep_space_catalog
    print(f"Loaded {len(catalog)} deep space celestial bodies.")
    print("First deep space object:", catalog[0])
