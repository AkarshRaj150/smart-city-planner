"""Analyses. Each returns inputs / formula / result / assumption (transparency requirement)."""
import math
from app import config

def classify_noise(db):
    t = config.NOISE_THRESHOLDS
    return "Low" if db < t["low"] else "Moderate" if db < t["moderate"] else "High" if db < t["high"] else "Very high"

def area(prop):
    b, t = prop["buildings"], prop["targets"]
    fp, fa = sum(x["footprint"] for x in b), sum(x["floor_area"] for x in b)
    built = fp / config.SITE_AREA * 100
    return {"inputs": {"site_area": config.SITE_AREA, "n_buildings": len(b)},
            "formula": "Built-up % = Footprint / Site Area x 100; FAR = Total Floor Area / Site Area",
            "result": {"footprint_m2": fp, "floor_area_m2": fa, "built_up_pct": built, "green_pct": t["green"],
                       "road_pct": t["road"], "open_space_pct": 100 - built - t["green"] - t["road"],
                       "far": fa / config.SITE_AREA},
            "assumption": "Green and road shares are planning targets; open space is the remainder."}

def carbon(prop):
    by_use = {}
    for x in prop["buildings"]:
        by_use[x["land_use"]] = by_use.get(x["land_use"], 0) + x["floor_area"] * config.CARBON_FACTORS[x["land_use"]]
    total = sum(by_use.values())
    fa = sum(x["floor_area"] for x in prop["buildings"])
    return {"inputs": {"factors_kgCO2e_m2": config.CARBON_FACTORS},
            "formula": "Carbon = Floor Area x Carbon Factor",
            "result": {"total_kgCO2e": total, "kg_per_m2": total / fa, "by_land_use": by_use},
            "assumption": "Planning-level estimate, not a verified lifecycle assessment."}

def solar(prop):
    k = config.SOLAR_IRRADIATION * config.SOLAR_EFFICIENCY * config.PERFORMANCE_FACTOR
    per = [{"building_id": x["building_id"], "kwh_year": x["footprint"] * config.USABLE_ROOF_FRACTION * k}
           for x in prop["buildings"]]
    total = sum(p["kwh_year"] for p in per)
    return {"inputs": {"irradiation": config.SOLAR_IRRADIATION, "efficiency": config.SOLAR_EFFICIENCY,
                       "performance_factor": config.PERFORMANCE_FACTOR},
            "formula": "Roof Area x Solar Irradiation x Efficiency x Performance Factor",
            "result": {"total_kwh_year": total, "kwh_per_site_m2": total / config.SITE_AREA,
                       "ranking": sorted(per, key=lambda p: -p["kwh_year"])[:10]},
            "assumption": "Usable roof = 60% of footprint; no shading applied. Estimated solar potential."}

def noise(prop, points):
    """Energy-sum of sources, each attenuated 20*log10(distance/10 m) (point-source spreading)."""
    res = []
    for b in prop["buildings"]:
        e = 0
        for p in points:
            d = max(math.hypot(b["cx"] - p["x"], b["cy"] - p["y"]), 10)
            e += 10 ** ((p["noise_db"] - 20 * math.log10(d / 10)) / 10)
        db = 10 * math.log10(e)
        res.append({"building_id": b["building_id"], "db": db, "category": classify_noise(db)})
    avg = sum(r["db"] for r in res) / len(res)
    return {"inputs": {"n_points": len(points), "thresholds_dB": config.NOISE_THRESHOLDS},
            "formula": "L = 10 log10( sum 10^((Li - 20 log10(d/10))/10) )",
            "result": {"average_db": avg, "affected_buildings": sum(r["category"] in ("High", "Very high") for r in res),
                       "buildings": res},
            "assumption": "Synthetic noise points; distance decay only, no barriers or reflections."}

def normalise(area_r, solar_r, noise_r):
    """Raw results -> 0-100 scores (higher = better) for the weighted indicator."""
    return {"land_efficiency": min(area_r["far"] / 5, 1) * 100,
            "solar": min(solar_r["kwh_per_site_m2"] / 100, 1) * 100,
            "noise": max(0, min(100, (85 - noise_r["average_db"]) / 45 * 100)),
            "green": min(area_r["green_pct"] / 25, 1) * 100}

def planning_index(scores, weights=None):
    """Sum(normalised metric x weight) / sum(weights of available metrics): the weighted planning indicator."""
    w = weights or config.ANALYSIS_WEIGHTS
    keys = [k for k in scores if w.get(k, 0) > 0]
    total = sum(w[k] for k in keys)
    return sum(scores[k] * w[k] for k in keys) / total if total else 0.0
