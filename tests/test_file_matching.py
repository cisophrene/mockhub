import os
import pytest
from fastapi.testclient import TestClient

def test_get_user_repos_sequence_happy_path(client: TestClient, scenario_root):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # First request should get the 001 file
    resp1 = github_client.get("/user/repos")
    assert resp1.status_code == 200
    assert resp1.json() == [{"id": 101, "name": "first-repo"}]

    # Second request should get the 002 file
    resp2 = github_client.get("/user/repos")
    assert resp2.status_code == 200
    assert resp2.json() == [{"id": 102, "name": "second-repo"}]

    # Third request should get the 003 file
    resp3 = github_client.get("/user/repos")
    assert resp3.status_code == 200
    assert resp3.json() == [{"id": 103, "name": "third-repo"}]

def test_trailing_slash_maps_to_index(client: TestClient, scenario_root):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request with trailing slash should map to _index file
    resp = github_client.get("/issues/")
    assert resp.status_code == 200
    assert resp.json() == []

def test_root_path_maps_to_index(client: TestClient, scenario_root):
    # Create a temporary scenario with root index file
    temp_scenario = "temp_root_index"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # Root path request should map to _index file
    resp = service_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_query_variant_matching_canonical_order(client: TestClient, scenario_root):

    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # First request with canonical order
    resp1 = github_client.get("/search?labels=bug&state=open")
    assert resp1.status_code == 200
    assert resp1.json() == {"items": [{"number": 42, "title": "Bug report"}]}

    # Second request with different order should still match the same file
    resp2 = github_client.get("/search?state=open&labels=bug")
    assert resp2.status_code == 200
    assert resp2.json() == {"items": [{"number": 42, "title": "Bug report"}]}

def test_body_predicate_filename_match(client: TestClient, scenario_root):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request with matching body
    resp = github_client.post(
        "/repos",
        json={"name": "my-repo"},
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 201
    assert resp.headers.get("X-MockHub") == "created"
    assert resp.json()["name"] == "my-repo"

def test_body_predicate_no_match_falls_through(client: TestClient):
    # Use a dedicated scenario for this test
    # Start session with body_predicate_fallback scenario
    client.post("/control/session/start", json={"scenario": "body_predicate_fallback"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request with non-matching body should fall through to hook
    resp = github_client.post(
        "/repos",
        json={"name": "other"},
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 422
    assert resp.headers.get("X-MockHub") == "fallback"
    assert "Invalid repository name" in resp.json()["message"]

def test_method_specific_routing(client: TestClient, scenario_root):
    # Create a temporary scenario with method-specific files
    temp_scenario = "temp_method_routing"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # GET request should get the GET payload
    get_resp = service_client.get("/foo")
    assert get_resp.status_code == 200
    assert get_resp.json() == {"method": "GET"}

    # POST request should get the POST payload
    post_resp = service_client.post("/foo")
    assert post_resp.status_code == 200
    assert post_resp.json() == {"method": "POST"}
