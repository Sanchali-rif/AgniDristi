from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine

from app.models.vnf_detection_model import VNFDetection
from app.models.thermal_object_model import ThermalObject
from app.models.firms_detection_model import FIRMSDetection
from app.models.alert_model import Alert
from app.models.monitoring_run_model import MonitoringRun

from app.controllers.object_controller import router as object_router
from app.controllers.monitoring_controller import router as monitoring_router
from app.routes.vnf import router as vnf_router
from app.routes.monitoring_runs import router as monitoring_runs_router
from app.routes.dashboard import (
    router as dashboard_router
)


app = FastAPI(
    title="Agni-Drishti API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(object_router)
app.include_router(monitoring_router)
app.include_router(vnf_router)
app.include_router(monitoring_runs_router)
app.include_router(
    dashboard_router
)

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Agni-Drishti backend is working"
    }