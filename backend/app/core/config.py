import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings:
    PROJECT_NAME: str = "AI-Powered Fault Prediction in 5G Testbed"
    TEAM_NAME: str = "Team Dynamites"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR.as_posix()}/data/5g_telemetry.db"
    )
    
    # Comma-separated origins are supplied by the deployment environment.
    # Keep local development origins as the default.
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]
    
    # Model Artifacts Path
    ARTIFACTS_DIR: Path = BASE_DIR / "artifacts" / "models"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # 5G Telemetry & ML Configuration
    HORIZON_STEPS: int = 15  # 15 time steps ahead for future fault prediction
    SAMPLING_INTERVAL_SECONDS: float = 2.0  # Simulator loop tick
    
    # Alert Configuration
    ALERT_COOLDOWN_SECONDS: int = 45
    RISK_THRESHOLD_LOW: float = 0.35
    RISK_THRESHOLD_MEDIUM: float = 0.60
    RISK_THRESHOLD_HIGH: float = 0.80
    ANOMALY_THRESHOLD: float = -0.05  # Isolation forest threshold
    
    # Sites and Cells
    DEFAULT_SITES: List[str] = ["SITE-01", "SITE-02", "SITE-03"]
    DEFAULT_CELLS: List[str] = ["CELL-01", "CELL-02", "CELL-03"]
    DEFAULT_COMPONENTS: List[str] = ["gNodeB-CU", "gNodeB-DU", "RU-RadioUnit", "5G-Core-UPF", "5G-Core-AMF"]

settings = Settings()

# Ensure directories exist
os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
