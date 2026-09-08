from pydantic import BaseModel, ConfigDict


class ThermalObjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    object_uid: str
    stage3_object_id: str | None

    latitude: float
    longitude: float

    classification_label: str | None
    classification_source: str | None
    predicted_label_confidence: float | None

    detection_count: int | None
    active_months: int | None
    persistence_ratio: float | None
    source_persistence_ratio: float | None
    temporal_source_hint: str | None
    tci: float | None
    seasonal_concentration: float | None

    temp_mean: float | None
    temp_median: float | None
    temp_min: float | None
    temp_max: float | None

    thermal_fingerprint: dict | None

    gas_flare_candidate: bool | None
    gas_flare_likelihood: str | None
    gas_flare_score: float | None
    gas_flare_source: str | None
    gas_flare_evidence: dict | None
