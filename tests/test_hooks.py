import os
import pytest
import re
import json
from fastapi.testclient import TestClient

def test_hook_handles_post_and_sets_state(client: TestClient):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # POST to /repos with a non-my-repo name should be handled by hook
    resp = github_client.post(
        "/repos",
        json={"name": "other"},
        headers={"Content-Type": "application/json"}
    )

    # Verify response
    assert resp.status_code == 200
    data = resp.json()

    # Check expected fields
    assert "id" in data
    assert data["name"] == "other"

    # Check created_at is ISO format
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", data["created_at"])

    # Check note mentions last_repo
    assert "Last repo: other" in data["note"]

def test_hook_none_falls_through_to_files(client: TestClient, scenario_root):
    # Create a temporary scenario with a hook that returns None
    temp_scenario = "temp_hook_none"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should be handled by file, not hook
    resp = service_client.get("/test")
    assert resp.status_code == 200
    assert resp.json() == {"source": "file"}

def test_hook_exception_returns_500(client: TestClient, scenario_root):
    # Create a temporary scenario with a hook that raises an exception
    temp_scenario = "temp_hook_error"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request to /error should trigger the exception and return 500
    resp = service_client.get("/error")
    assert resp.status_code == 500
    assert "Hook error" in resp.json()["detail"]
    assert "Intentional error" in resp.json()["detail"]

def test_hook_transform_modifies_payload(client: TestClient):
    # Create a temporary scenario with a transform hook
    temp_scenario = "temp_hook_transform"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should be handled by file, then transformed by hook
    resp = service_client.get("/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "file"
    assert data["transformed"] is True
    assert "added_by_hook" in data
