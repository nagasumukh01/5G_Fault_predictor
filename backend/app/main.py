from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base
from backend.app.api.router import api_router
from backend.app.api.endpoints.health import health_check
from backend.app.integrations.prometheus_exporter import get_prometheus_metrics
from backend.app.ml.pipeline import model_pipeline
from backend.app.services.simulator_service import simulator_service

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print(f"[{settings.PROJECT_NAME}] Starting up...")
    loaded = model_pipeline.load_models_if_present()
    if loaded:
        print("[ML Engine] Pretrained models loaded successfully from disk.")
    else:
        print("[ML Engine] Pretrained models not found; will train or run fallback.")

    # Automatically start simulator so telemetry flows immediately
    simulator_service.start()

    yield

    # Shutdown actions
    print(f"[{settings.PROJECT_NAME}] Shutting down...")
    simulator_service.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI-powered 5G fault prediction and anomaly detection platform for telecom testbeds.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration for local Vite (5173, 3000) and Vercel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check endpoint
@app.get("/health", tags=["Health"])
def root_health():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs"
    }

# Prometheus metrics endpoint
@app.get("/metrics", tags=["Observability"])
def prometheus_metrics():
    content, content_type = get_prometheus_metrics()
    return Response(content=content, media_type=content_type)

# Mount API V1
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
