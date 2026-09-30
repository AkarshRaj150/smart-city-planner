# SmartCity Planner (prototype) - SIH26114, Team Aero-Metric

Early-stage planning decision-support prototype. **DEMO / SYNTHETIC DATA** (fictional "Aero-Metric Smart District", Delhi NCR).
Not Autodesk Forma, not CFD, not real Delhi data, not engineering certification.

## Status
Built: backend core (FastAPI), synthetic data generator, Proposal A/B generation, Area, Carbon, Solar-energy and Noise
analyses (each with inputs/formula/result/assumption), weighted planning indicator, 11 passing tests.
NOT built yet: React frontend and maps, database (SQLAlchemy), PDF report, upload validation, and the sun, daylight,
wind, microclimate and mobility analyses.

## Install (Windows PowerShell, Python 3.11+)
    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python seed_data.py
    python -m pytest

## Run
    uvicorn app.main:app --reload
Open http://127.0.0.1:8000/docs and try:
- /api/proposals
- /api/analysis/area/A  (also carbon, solar, noise; A or B)
- /api/comparison?w_solar=40   (change weights, watch the indicator move)

Settings (carbon factors, solar efficiency, thresholds, weights) are in `backend/app/config.py`.
