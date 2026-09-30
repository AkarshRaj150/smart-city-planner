"""Run: python seed_data.py  -> writes demo data into ../data"""
import csv, os
from app.services import site_service as s
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"); os.makedirs(out, exist_ok=True)
s.export_geojson(out)
with open(f"{out}/noise_data.csv", "w", newline="") as f:
    w = csv.DictWriter(f, ["location_id", "x", "y", "noise_db", "source"]); w.writeheader(); w.writerows(s.get_noise_points())
with open(f"{out}/sample_terrain.csv", "w", newline="") as f:
    csv.writer(f).writerows(s.get_terrain())
print("Demo data written (DEMO / SYNTHETIC DATA) to", os.path.abspath(out))
