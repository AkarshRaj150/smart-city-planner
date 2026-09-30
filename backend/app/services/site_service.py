"""Builds the synthetic 'Aero-Metric Smart District' (local metre coordinates 0..1000)."""
import math, random, json
from shapely.geometry import box, mapping, LineString
from app import config

def to_lonlat(x, y):
    """Convert local metres to lon/lat around the fictional site centre."""
    lat = config.ORIGIN_LAT + (y - 500) / 111_320
    lon = config.ORIGIN_LON + (x - 500) / (111_320 * math.cos(math.radians(config.ORIGIN_LAT)))
    return [lon, lat]

def geom_lonlat(g):
    """Shapely geometry (metres) -> GeoJSON geometry (lon/lat)."""
    m = mapping(g)
    if m["type"] == "Polygon":
        m["coordinates"] = [[to_lonlat(*p) for p in ring] for ring in m["coordinates"]]
    else:
        m["coordinates"] = [to_lonlat(*p) for p in m["coordinates"]]
    return m

def get_roads():
    roads = [("R01", "MAIN", 30, [(0, 500), (1000, 500)])]
    for i, x in enumerate((250, 500, 750)):
        roads.append((f"R{i+2:02d}", "SECONDARY", 20, [(x, 0), (x, 1000)]))
    n = 5
    for y in (200, 350, 650, 800):
        roads.append((f"R{n:02d}", "LOCAL", 10, [(0, y), (1000, y)])); n += 1
    for x in (125, 375, 625, 875):
        roads.append((f"R{n:02d}", "LOCAL", 10, [(x, 0), (x, 1000)])); n += 1
    return [{"road_id": r, "road_type": t, "width": w, "length": LineString(c).length, "coords": c}
            for r, t, w, c in roads]

def get_noise_points(seed=42):
    rnd = random.Random(seed)
    pts = []
    for i in range(25):
        src = rnd.choice(["traffic", "commercial", "construction", "quiet zone"])
        base = {"traffic": 78, "commercial": 68, "construction": 82, "quiet zone": 45}[src]
        x, y = (rnd.uniform(0, 1000), 500 + rnd.uniform(-40, 40)) if src == "traffic" else \
               (rnd.uniform(0, 1000), rnd.uniform(0, 1000))
        pts.append({"location_id": f"N{i+1:02d}", "x": round(x, 1), "y": round(y, 1),
                    "noise_db": round(base + rnd.uniform(-3, 3), 1), "source": src})
    return pts

def get_terrain(n=20):
    """Gentle synthetic terrain (about 190-225 m) as an n x n grid."""
    return [[round(207 + 17 * math.sin(i / n * math.pi) * math.cos(j / n * math.pi * 0.8), 1)
             for j in range(n)] for i in range(n)]

def get_site():
    return {"name": "Aero-Metric Smart District", "label": config.DATA_LABEL, "area_m2": config.SITE_AREA,
            "boundary": geom_lonlat(box(0, 0, 1000, 1000)),
            "roads": get_roads(), "noise_points": get_noise_points()}

def export_geojson(folder):
    """Used by seed_data.py to write demo files."""
    feats = [{"type": "Feature", "properties": {k: v for k, v in r.items() if k != "coords"},
              "geometry": geom_lonlat(LineString(r["coords"]))} for r in get_roads()]
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{folder}/sample_roads.geojson", "w"))
    json.dump({"type": "Feature", "properties": {"name": "Aero-Metric Smart District", "label": config.DATA_LABEL},
               "geometry": geom_lonlat(box(0, 0, 1000, 1000))}, open(f"{folder}/sample_site.geojson", "w"))
