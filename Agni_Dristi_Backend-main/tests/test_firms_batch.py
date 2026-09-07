import pandas as pd

from app.core.database import SessionLocal
from app.services.firms.firms_batch_service import process_firms_dataframe


df = pd.DataFrame([
    {
        "latitude": 23.66800,
        "longitude": 86.92300,
        "bright_ti4": 345.2,
        "bright_ti5": 310.5,
        "frp": 12.4,
        "scan": 0.45,
        "track": 0.48,
        "acq_date": "2026-09-06",
        "acq_time": "2142",
        "satellite": "N",
        "instrument": "VIIRS",
        "confidence": "nominal",
        "version": "2.0NRT",
        "daynight": "N"
    },
    {
        "latitude": 24.10000,
        "longitude": 87.50000,
        "bright_ti4": 330.1,
        "bright_ti5": 305.2,
        "frp": 8.6,
        "scan": 0.50,
        "track": 0.48,
        "acq_date": "2026-09-06",
        "acq_time": "2145",
        "satellite": "N",
        "instrument": "VIIRS",
        "confidence": "nominal",
        "version": "2.0NRT",
        "daynight": "N"
    }
])

df["acq_date"] = pd.to_datetime(df["acq_date"]).dt.date

db = SessionLocal()

try:
    result = process_firms_dataframe(db, df)
    print(result)

finally:
    db.close()