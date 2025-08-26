import os
import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client: TestClient):
    response = client.get("/control/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_status_endpoint_without_session(client: TestClient):
    response = client.get("/control/status")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] is None
    assert data["scenario"] is None
    assert data["sequences"] == {}

def test_start_session_with_valid_scenario(client: TestClient):
    response = client.post("/control/session/start", json={"scenario": "test_scenario"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["scenario"] == "test_scenario"
    assert data["session_id"].startswith("s-")

def test_start_session_with_invalid_scenario(client: TestClient):
    response = client.post("/control/session/start", json={"scenario": "non_existent_scenario"})
    assert response.status_code == 404
    assert "Scenario not found" in response.json()["detail"]

def test_reset_session_keeps_scenario_by_default(client: TestClient):
    # Start with a valid scenario under tests/scenarios
    start = client.post("/control/session/start", json={"scenario": "test_scenario"})
    assert start.status_code == 200
    orig = start.json()
    # Reset without body -> scenario unchanged, session_id changed
    reset = client.post("/control/session/reset")
    assert reset.status_code == 200
    r = reset.json()
    assert r["scenario"] == orig["scenario"]
    assert r["session_id"].startswith("s-")
    assert r["session_id"] != orig["session_id"]

def test_reset_session_switches_scenario(client: TestClient, scenario_root: str):
    # Ensure a second, empty scenario exists
    new_scn = "new_temp_scenario"
    os.makedirs(os.path.join(scenario_root, new_scn), exist_ok=True)
    # Start with test_scenario
    start = client.post("/control/session/start", json={"scenario": "test_scenario"})
    assert start.status_code == 200
    # Switch to the new scenario
    reset = client.post("/control/session/reset", json={"scenario": new_scn})
    assert reset.status_code == 200
    r = reset.json()
    assert r["scenario"] == new_scn
    assert r["session_id"].startswith("s-")

def test_service_call_without_session_fails(client: TestClient):
    # Hitting a service port (github on 27001) with no active session should 400
    # Reset global state to ensure no session is active
    from src.mockhub.app import GLOBAL
    GLOBAL.current = None
    
    service_client = TestClient(client.app, base_url="http://testserver:27001")
    resp = service_client.get("/user/repos")
    assert resp.status_code == 400
    assert "No active session" in resp.json().get("detail", "")
