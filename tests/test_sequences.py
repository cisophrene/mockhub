import os
import pytest
from fastapi.testclient import TestClient

def test_sequence_counters_increment_and_report_in_status(client: TestClient):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Call GET /user/repos twice
    resp1 = github_client.get("/user/repos")
    assert resp1.status_code == 200
    assert resp1.json() == [{"id": 101, "name": "first-repo"}]

    resp2 = github_client.get("/user/repos")
    assert resp2.status_code == 200
    assert resp2.json() == [{"id": 102, "name": "second-repo"}]

    # Check status endpoint to verify sequence counter
    status_resp = client.get("/control/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()

    # Verify sequence counter is present and has the correct value (3 for next index)
    assert "sequences" in status_data
    assert "GET/user/repos" in status_data["sequences"]
    assert status_data["sequences"]["GET/user/repos"] == 3

def test_sequence_exhaustion_returns_410(client: TestClient):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Call GET /user/repos three times (consuming all available files)
    for i in range(3):
        resp = github_client.get("/user/repos")
        assert resp.status_code == 200

    # Fourth call should result in 410 Gone (sequence exhausted)
    resp4 = github_client.get("/user/repos")
    assert resp4.status_code == 410
    assert "sequence exhausted" in resp4.json()["detail"]
    assert "004" in resp4.json()["detail"]  # Should mention the index

def test_reset_session_resets_sequences(client: TestClient):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Consume the sequence
    for i in range(3):
        resp = github_client.get("/user/repos")
        assert resp.status_code == 200

    # Reset session with same scenario
    client.post("/control/session/reset", json={"scenario": "github_repo_flow"})

    # Should be able to get the first file again
    resp = github_client.get("/user/repos")
    assert resp.status_code == 200
    assert resp.json() == [{"id": 101, "name": "first-repo"}]

def test_sequences_are_keyed_by_query_body_variant(client: TestClient, scenario_root):
    # Create a temporary scenario with query variants
    temp_scenario = "temp_sequence_variants"
    service_dir = os.path.join(scenario_root, temp_scenario, "github", "GET")

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Call each variant twice
    base1 = github_client.get("/items")
    assert base1.status_code == 200
    assert base1.json() == {"variant": "base", "seq": 1}

    query1 = github_client.get("/items?type=a")
    assert query1.status_code == 200
    assert query1.json() == {"variant": "type_a", "seq": 1}

    base2 = github_client.get("/items")
    assert base2.status_code == 200
    assert base2.json() == {"variant": "base", "seq": 2}

    query2 = github_client.get("/items?type=a")
    assert query2.status_code == 200
    assert query2.json() == {"variant": "type_a", "seq": 2}

    # Check status to verify independent counters
    status_resp = client.get("/control/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()

    # Verify sequence counters are separate
    assert "GET/items" in status_data["sequences"]
    assert status_data["sequences"]["GET/items"] == 3

    assert "GET/items__q.type=a" in status_data["sequences"]
    assert status_data["sequences"]["GET/items__q.type=a"] == 3
