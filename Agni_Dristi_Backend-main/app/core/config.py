import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
GEO_DATA_DIR = DATA_DIR / "geo"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

VNF_DATA_PATH = RAW_DATA_DIR / "VNF_INDIA_2026.csv"

INDIA_BOUNDARY_PATH = (
    GEO_DATA_DIR / "india_boundary.geojson"
)

MODEL_PATH = (
    ARTIFACTS_DIR
    / "PAN_INDIA_XGBOOST_THERMAL_VARIABILITY.pkl"
)


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY")
    GEM_PRIMARY_RADIUS_METERS = float(
        os.getenv("GEM_PRIMARY_RADIUS_METERS", "1000")
    )
    GEM_FALLBACK_RADIUS_METERS = float(
        os.getenv("GEM_FALLBACK_RADIUS_METERS", "3000")
    )
    GEM_MAX_RADIUS_METERS = float(
        os.getenv("GEM_MAX_RADIUS_METERS", "5000")
    )
    GEM_EXTENDED_RADIUS_METERS = float(
        os.getenv("GEM_EXTENDED_RADIUS_METERS", "10000")
    )


settings = Settings()
