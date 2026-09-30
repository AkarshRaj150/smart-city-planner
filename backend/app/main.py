"""FastAPI app. Run: uvicorn app.main:app --reload   (interactive docs at /docs)"""
from functools import lru_cache
from fastapi import FastAPI, HTTPException
from app import config
from app.services import site_service, proposal_service, analysis_service as an

app = FastAPI(title="SmartCity Planner (prototype)")

@lru_cache(maxsize=None)          # cache: each proposal is generated once
def _prop(pid):
    if pid not in proposal_service.PROPOSALS:
        raise HTTPException(404, "Unknown proposal. Use A or B.")
    return proposal_service.generate(pid)

@lru_cache(maxsize=None)          # cache: each analysis is computed once
def _analysis(kind, pid):
    p, pts = _prop(pid), site_service.get_noise_points()
    return {"area": lambda: an.area(p), "carbon": lambda: an.carbon(p),
            "solar": lambda: an.solar(p), "noise": lambda: an.noise(p, pts)}[kind]()

@app.get("/api/site")
def site(): return site_service.get_site()

@app.get("/api/proposals")
def proposals(): return [_prop(i) for i in proposal_service.PROPOSALS]

@app.get("/api/analysis/{kind}/{pid}")
def analysis(kind: str, pid: str):
    if kind not in ("area", "carbon", "solar", "noise"):
        raise HTTPException(501, f"Analysis '{kind}' is not implemented yet.")
    return _analysis(kind, pid.upper())

@app.get("/api/comparison")
def comparison(w_land: float = None, w_solar: float = None, w_noise: float = None, w_green: float = None):
    weights = dict(config.ANALYSIS_WEIGHTS)
    for k, v in (("land_efficiency", w_land), ("solar", w_solar), ("noise", w_noise), ("green", w_green)):
        if v is not None: weights[k] = v
    out = {}
    for pid in ("A", "B"):
        a, s, n = (_analysis(k, pid)["result"] for k in ("area", "solar", "noise"))
        sc = an.normalise(a, s, n)
        out[pid] = {"scores": sc, "weighted_planning_indicator": an.planning_index(sc, weights)}
    return {"weights": weights, "results": out,
            "note": "Weighted planning indicator, not an objective 'best design'. Changing weights changes the result. "
                    "Only 4 of the 8 criteria are implemented so far; weights are re-normalised over those.",
            "disclaimer": config.DISCLAIMER}
