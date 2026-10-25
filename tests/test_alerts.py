import pytest
from backend.app.db.session import SessionLocal, Base, engine
from backend.app.services.alert_service import alert_service
from backend.app.models.entities import AlertRecord

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_alert_lifecycle(db_session):
    # 1. Create Alert
    alert = alert_service.create_or_update_alert(
        db=db_session,
        site_id="TEST-SITE",
        cell_id="TEST-CELL",
        component_id="gNodeB-CU",
        severity="CRITICAL",
        fault_type="radio_degradation",
        risk_score=0.88,
        anomaly_score=-0.22,
        metrics_snapshot={"rsrp_dbm": -125.0},
        top_features=["rsrp_dbm", "sinr_db"],
        recommended_actions=["Inspect RU cabling"]
    )
    assert alert is not None
    assert alert.status == "ACTIVE"
    alert_id = alert.alert_id

    # 2. Acknowledge Alert
    ack = alert_service.acknowledge_alert(
        db=db_session,
        alert_id=alert_id,
        operator_name="Test Operator",
        notes="Under review"
    )
    assert ack.status == "ACKNOWLEDGED"
    assert ack.acknowledged_by == "Test Operator"

    # 3. Resolve Alert
    res = alert_service.resolve_alert(
        db=db_session,
        alert_id=alert_id,
        operator_name="Test Operator",
        resolution_notes="Power cycle successful"
    )
    assert res.status == "RESOLVED"
    assert res.resolved_at is not None
