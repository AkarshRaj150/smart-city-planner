"""All tunable settings in one place (edit here, no other file needs changing)."""
SITE_AREA = 1_000_000            # m2 (1 km x 1 km planning boundary)
DEFAULT_BUILDING_HEIGHT = 12.0   # m, used when a building has no height
FLOOR_HEIGHT = 4.0               # m per floor
ORIGIN_LAT, ORIGIN_LON = 28.6139, 77.2090   # fictional site centre (Delhi NCR)
CARBON_FACTORS = {"residential": 500, "commercial": 650, "institutional": 550, "mixed_use": 600}  # kg CO2e/m2
SOLAR_IRRADIATION = 1700         # kWh/m2/year (demo value)
SOLAR_EFFICIENCY = 0.20
PERFORMANCE_FACTOR = 0.80
USABLE_ROOF_FRACTION = 0.6
NOISE_THRESHOLDS = {"low": 50, "moderate": 65, "high": 75}   # dB
ANALYSIS_WEIGHTS = {"land_efficiency": 15, "solar": 15, "daylight": 15, "wind": 10,
                    "microclimate": 15, "noise": 10, "mobility": 10, "green": 10}
DATA_LABEL = "DEMO / SYNTHETIC DATA"
DISCLAIMER = ("This application is an early-stage planning decision-support prototype. Environmental "
              "indicators are calculated using simplified or synthetic models for demonstration purposes "
              "and should not be treated as professional engineering, environmental, CFD, energy, acoustic, "
              "or regulatory certification.")
