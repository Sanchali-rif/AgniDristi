from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.thermal_object_model import ThermalObject
from app.schemas.thermal_object_schema import ThermalObjectResponse


router = APIRouter(
    prefix="/objects",
    tags=["Thermal Objects"]
)


@router.get("/",response_model=list[ThermalObjectResponse])
def get_objects(
    class_name: str | None = None,
    min_confidence: float | None = Query(default=None, ge=0, le=1),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(ThermalObject)

    if class_name:
        query = query.filter(
            ThermalObject.classification_label == class_name
        )

    if min_confidence is not None:
        query = query.filter(
            ThermalObject.predicted_label_confidence
            >= min_confidence
        )

    objects = query.limit(limit).all()

    return objects