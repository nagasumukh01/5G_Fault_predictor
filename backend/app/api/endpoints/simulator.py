from fastapi import APIRouter
from backend.app.schemas.simulator import ScenarioTriggerRequest, ScenarioResponse, SimulatorStatusResponse
from backend.app.services.simulator_service import simulator_service

router = APIRouter()

@router.get("/simulator/status", response_model=SimulatorStatusResponse)
def get_simulator_status():
    status_dict = simulator_service.get_status()
    return SimulatorStatusResponse(**status_dict)

@router.post("/simulator/start")
def start_simulator():
    simulator_service.start()
    return {"status": "SUCCESS", "message": "5G Telemetry & Fault Simulator started."}

@router.post("/simulator/stop")
def stop_simulator():
    simulator_service.stop()
    return {"status": "SUCCESS", "message": "5G Telemetry & Fault Simulator stopped."}

@router.post("/simulator/scenario", response_model=ScenarioResponse)
def trigger_scenario(req: ScenarioTriggerRequest):
    scenario_id = simulator_service.trigger_scenario(
        scenario_type=req.scenario_type,
        target_site=req.target_site,
        target_cell=req.target_cell,
        target_component=req.target_component,
        duration_seconds=req.duration_seconds,
        severity=req.severity
    )
    # Auto start simulator if not already running so data streams immediately
    if not simulator_service.is_running:
        simulator_service.start()

    return ScenarioResponse(
        status="ACTIVE",
        scenario_id=scenario_id,
        scenario_type=req.scenario_type,
        target_site=req.target_site,
        target_cell=req.target_cell,
        target_component=req.target_component,
        duration_seconds=req.duration_seconds,
        severity=req.severity,
        message=f"Scenario '{req.scenario_type}' injected on {req.target_site}/{req.target_cell} ({req.target_component}) for {req.duration_seconds}s."
    )
