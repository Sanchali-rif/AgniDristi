from datetime import date

from app.core.database import SessionLocal
from app.services.firms.firms_monitor_service import process_firms_detection


db = SessionLocal()

try:
    row = {
        "latitude": 23.66800,
        "longitude": 86.92300,
        "bright_ti4": 345.2,
        "bright_ti5": 310.5,
        "frp": 12.4,
        "scan": 0.45,
        "track": 0.48,
        "acq_date": date(2026, 9, 6),
        "acq_time": "2142",
        "satellite": "N",
        "instrument": "VIIRS",
        "confidence": "nominal",
        "version": "2.0NRT",
        "daynight": "N"
    }

    result = process_firms_detection(db, row)

    print(result)

finally:
    db.close()