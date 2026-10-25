from fastapi import APIRouter
from backend.app.api.endpoints import health, metrics, predictions, alerts, models, simulator

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(metrics.router, tags=["5G Telemetry Metrics"])
api_router.include_router(predictions.router, tags=["ML Predictions"])
api_router.include_router(alerts.router, tags=["Alert Management"])
api_router.include_router(models.router, tags=["ML Models & Evaluation"])
api_router.include_router(simulator.router, tags=["5G Testbed Simulator"])
