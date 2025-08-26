import os
import pytest
import re
import uuid
from fastapi.testclient import TestClient

def test_jinja_renders_with_request_context(client: TestClient):
    # Start session with jinja_template_test scenario
    client.post("/control/session/start", json={"scenario": "jinja_template_test"})
    
    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")
    
    # POST to /repos with a template-rendered response
    resp = github_client.post(
        "/repos",
        json={"name": "templ"},
        headers={"Content-Type": "application/json"}
    )
    
    # Verify response
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/json"
    data = resp.json()
    
    # Check expected fields
    assert "id" in data
    assert data["name"] == "templ"
    
    # Check created_at is ISO format
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", data["created_at"])
    
    # Check note mentions last_repo
    assert "Last repo: " in data["note"]

def test_jinja_strictundefined_causes_500(client: TestClient, scenario_root):
    # Create a temporary scenario with a template that references undefined variable
    temp_scenario = "temp_jinja_error"
    service_dir = os.path.join(scenario_root, temp_scenario, "github")
    os.makedirs(os.path.join(service_dir, "GET"), exist_ok=True)
    
    # Create a template file with an undefined variable
    with open(os.path.join(service_dir, "GET", "error.json.j2"), "w") as f:
        f.write('{"error": "{{ not_defined }}"}')
    
    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})
    
    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")
    
    # Request should fail with 500 due to undefined variable
    resp = service_client.get("/error")
    assert resp.status_code == 500
    assert "undefined" in resp.json()["detail"].lower()
