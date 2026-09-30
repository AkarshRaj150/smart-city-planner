"""Generates Proposal A (compact) and B (green) on the SAME site, programmatically."""
import math
from shapely.geometry import box
from app import config
from app.services.site_service import geom_lonlat

# Land-use targets (% of site). Building footprint is derived from 'built'.
PROPOSALS = {
    "A": {"name": "Proposal A - Compact Development", "built": 55, "green": 15, "road": 10,
          "grid": (7, 7), "floors": (10, 16)},
    "B": {"name": "Proposal B - Green / Open Development", "built": 40, "green": 20, "road": 10,
          "grid": (6, 7), "floors": (4, 8)},
}

def land_use_for(i, y):
    """Mixed-use/commercial along the main road (y=500), residential elsewhere, some institutional."""
    if abs(y - 500) < 200:
        return "mixed_use" if i % 2 else "commercial"
    return "institutional" if i % 6 == 0 else "residential"

def generate(pid):
    p = PROPOSALS[pid]
    cols, rows = p["grid"]
    n = cols * rows
    side = math.sqrt(config.SITE_AREA * p["built"] / 100 / n)   # total footprint hits the target %
    buildings = []
    for r in range(rows):
        for c in range(cols):
            i = len(buildings)
            cx, cy = (c + 0.5) * 1000 / cols, (r + 0.5) * 1000 / rows
            floors = p["floors"][0] + (i * 7) % (p["floors"][1] - p["floors"][0] + 1)   # varied, deterministic
            geom = box(cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2)
            buildings.append({"building_id": f"B{i+1:03d}", "cx": cx, "cy": cy, "side": side,
                              "land_use": land_use_for(i, cy), "floors": floors,
                              "height": floors * config.FLOOR_HEIGHT, "footprint": geom.area,
                              "floor_area": geom.area * floors, "occupancy_estimate": int(geom.area * floors / 30),
                              "geometry": geom_lonlat(geom)})
    return {"id": pid, "name": p["name"], "targets": p, "buildings": buildings}
