from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.ml.pipeline import model_pipeline

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "online" if db_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "version": settings.VERSION,
        "database": "connected" if db_ok else "unreachable",
        "ml_engine": "loaded" if model_pipeline.is_loaded else "uninitialized"
    }
