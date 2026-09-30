import json, pytest
from app import config
from app.services import proposal_service as ps, analysis_service as an, site_service as ss
A, B = ps.generate("A"), ps.generate("B")

def test_building_counts(): assert 40 <= len(A["buildings"]) <= 60 and 40 <= len(B["buildings"]) <= 60
def test_area_built_pct_a(): assert an.area(A)["result"]["built_up_pct"] == pytest.approx(55, abs=0.1)
def test_area_built_pct_b(): assert an.area(B)["result"]["built_up_pct"] == pytest.approx(40, abs=0.1)
def test_percentages_sum():
    r = an.area(A)["result"]
    assert r["built_up_pct"] + r["open_space_pct"] + r["green_pct"] + r["road_pct"] == pytest.approx(100)
def test_far_a_higher(): assert an.area(A)["result"]["far"] > an.area(B)["result"]["far"]
def test_carbon_formula():
    b = A["buildings"][0]
    assert an.carbon({"buildings": [b]})["result"]["total_kgCO2e"] == pytest.approx(b["floor_area"] * config.CARBON_FACTORS[b["land_use"]])
def test_solar_formula():
    r = an.solar({"buildings": [{"building_id": "X", "footprint": 1000}]})["result"]["total_kwh_year"]
    assert r == pytest.approx(1000 * 0.6 * 1700 * 0.2 * 0.8)
def test_noise_classification():
    assert [an.classify_noise(x) for x in (40, 60, 70, 80)] == ["Low", "Moderate", "High", "Very high"]
def test_weighted_score_changes_with_weights():
    sc = {"solar": 100, "green": 0}
    assert an.planning_index(sc, {"solar": 1, "green": 1}) == 50
    assert an.planning_index(sc, {"solar": 3, "green": 1}) == 75
def test_weighted_score_empty(): assert an.planning_index({}, {}) == 0.0
def test_geojson_seed_valid(tmp_path):
    ss.export_geojson(str(tmp_path)); d = json.load(open(tmp_path / "sample_roads.geojson"))
    assert len(d["features"]) == 12 and d["features"][0]["properties"]["road_type"] == "MAIN"
