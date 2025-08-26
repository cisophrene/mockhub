import os
import pytest
from fastapi.testclient import TestClient

def test_wildcard_matching_in_path_segments(client: TestClient, scenario_root):
    # Create a temporary scenario with wildcard path matching
    temp_scenario = "temp_wildcard_matching"
    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Test wildcard matching for repos issues
    resp1 = github_client.get("/repos/octocat/hello-world/issues")
    assert resp1.status_code == 200
    assert resp1.json() == {"owner": "octocat", "repo": "hello-world", "issues": []}

    # Test wildcard matching for user repos with Jinja2 template
    resp2 = github_client.get("/users/john/repos")
    assert resp2.status_code == 200
    data = resp2.json()
    assert len(data) == 2
    assert data[0]["name"] == "john-repo-1"
    assert data[1]["name"] == "john-repo-2"

def test_wildcard_matching_falls_back_to_files_when_no_rules(client: TestClient, scenario_root):
    # Create a temporary scenario with direct file wildcard matching (no rules)
    temp_scenario = "temp_wildcard_files"
    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should match the wildcard file path directly
    resp = github_client.get("/repos/testuser/testrepo/issues")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Wildcard matched for testuser/testrepo"
