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
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'app.db'}"
    )
    FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY")


settings = Settings()